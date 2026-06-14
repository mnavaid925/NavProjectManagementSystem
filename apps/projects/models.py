"""Projects workspace models (tenant-scoped) powering the reference dashboard."""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]


class Project(models.Model):
    """A project owned by a tenant."""

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=160)
    code = models.CharField(max_length=40, blank=True)
    client_name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress = models.PositiveSmallIntegerField(default=0)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    spent = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='owned_projects',
    )
    is_billable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def budget_used_percent(self):
        if not self.budget:
            return 0
        return min(int(round(float(self.spent) / float(self.budget) * 100)), 100)


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tasks',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Meeting(models.Model):
    MEETING_TYPE_CHOICES = [
        ('standup', 'Standup'),
        ('review', 'Review'),
        ('planning', 'Planning'),
        ('client', 'Client'),
        ('retro', 'Retrospective'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=200)
    meeting_type = models.CharField(max_length=12, choices=MEETING_TYPE_CHOICES, default='standup')
    scheduled_for = models.DateTimeField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField(default=30)
    location = models.CharField(max_length=200, blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='organized_meetings',
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='meetings',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_for']

    def __str__(self):
        return self.title


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES
    CATEGORY_CHOICES = [
        ('bug', 'Bug'),
        ('feature', 'Feature'),
        ('support', 'Support'),
        ('question', 'Question'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='tickets')
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets',
    )
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='support')
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='requested_tickets',
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tickets',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.subject


class ProjectInvoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='project_invoices')
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices',
    )
    number = models.CharField(max_length=20, unique=True)
    client_name = models.CharField(max_length=160, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    tax = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    status = models.CharField(max_length=14, choices=STATUS_CHOICES, default='draft')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(default=timezone.now)
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        if not self.total:
            self.total = (self.amount or Decimal('0')) + (self.tax or Decimal('0'))
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = ProjectInvoice.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'PINV-{seq:05d}'
        while ProjectInvoice.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'PINV-{seq:05d}'
        return candidate

    @property
    def balance_due(self):
        return (self.total or Decimal('0')) - (self.paid_amount or Decimal('0'))


class FinancialSnapshot(models.Model):
    """A monthly income/expense snapshot (seed-only; no UI forms)."""

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='financial_snapshots')
    period = models.CharField(max_length=10)  # e.g. '2026-06'
    income = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    expense = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['period']
        unique_together = ('tenant', 'period')

    def __str__(self):
        return f'{self.tenant} {self.period}'
