"""Time & Attendance Tracking models (tenant-scoped).

Covers timesheets and their daily lines, multi-level timesheet approvals,
leave records, and per-period utilization snapshots.
"""
from decimal import Decimal  # noqa: F401  (kept for convention parity across modules)

from django.conf import settings
from django.db import models
from django.utils import timezone


class Timesheet(models.Model):
    """A weekly/periodic timesheet for an owner, auto-number TS-00001."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='timesheets',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='timesheets',
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='timesheets',
    )
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    total_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    billable_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_start', '-id']

    def __str__(self):
        owner = self.owner.get_full_name() if self.owner else 'Unassigned'
        return f'{self.number} — {owner}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Timesheet.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'TS-{seq:05d}'
        while Timesheet.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'TS-{seq:05d}'
        return candidate


class TimesheetLine(models.Model):
    """A single dated time entry on a timesheet."""

    ACTIVITY_CHOICES = [
        ('development', 'Development'),
        ('meeting', 'Meeting'),
        ('review', 'Review'),
        ('admin', 'Administration'),
        ('support', 'Support'),
        ('research', 'Research'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='timesheet_lines',
    )
    timesheet = models.ForeignKey(
        Timesheet, on_delete=models.CASCADE, related_name='lines',
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='timesheet_lines',
    )
    work_date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    activity = models.CharField(max_length=16, choices=ACTIVITY_CHOICES, default='development')
    is_billable = models.BooleanField(default=True)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-work_date', '-id']

    def __str__(self):
        return f'{self.timesheet} — {self.work_date} ({self.hours}h)'


class TimesheetApproval(models.Model):
    """A multi-level approval decision for a timesheet."""

    DECISION_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='timesheet_approvals',
    )
    timesheet = models.ForeignKey(
        Timesheet, on_delete=models.CASCADE, related_name='approvals',
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='timesheet_approvals',
    )
    decision = models.CharField(max_length=12, choices=DECISION_CHOICES, default='pending')
    level = models.PositiveSmallIntegerField(default=1)
    comments = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.timesheet} — {self.get_decision_display()}'


class LeaveRecord(models.Model):
    """A leave/time-off request for an owner, auto-number LV-00001."""

    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('parental', 'Parental Leave'),
        ('bereavement', 'Bereavement'),
        ('toil', 'Time Off in Lieu'),
    ]
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='leave_records',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leave_records',
    )
    leave_type = models.CharField(max_length=16, choices=LEAVE_TYPE_CHOICES, default='annual')
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='requested')
    reason = models.CharField(max_length=200, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_leave_records',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', '-id']

    def __str__(self):
        owner = self.owner.get_full_name() if self.owner else 'Unassigned'
        return f'{self.number} — {owner}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = LeaveRecord.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'LV-{seq:05d}'
        while LeaveRecord.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'LV-{seq:05d}'
        return candidate


class UtilizationSnapshot(models.Model):
    """A per-period capacity/utilization snapshot for an owner."""

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='utilization_snapshots',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='utilization_snapshots',
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='utilization_snapshots',
    )
    period = models.CharField(max_length=10)
    capacity_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    billable_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    non_billable_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    utilization_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period', '-id']

    def __str__(self):
        owner = self.owner.get_full_name() if self.owner else 'Unassigned'
        return f'{owner} — {self.period}'
