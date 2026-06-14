"""Resource Management models (tenant-scoped): skills, resources, allocations,
team assignments, demand forecasts, and time entries."""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Skill(models.Model):
    """A capability that a resource can possess (skills inventory)."""

    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('functional', 'Functional'),
        ('soft', 'Soft Skill'),
        ('domain', 'Domain'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='resources_skills')
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='technical')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Resource(models.Model):
    """A person, contractor, or piece of equipment in the resource pool."""

    RESOURCE_TYPE_CHOICES = [
        ('employee', 'Employee'),
        ('contractor', 'Contractor'),
        ('equipment', 'Equipment'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='resources_resources')
    name = models.CharField(max_length=150)
    resource_type = models.CharField(max_length=12, choices=RESOURCE_TYPE_CHOICES, default='employee')
    email = models.EmailField(blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    capacity_hours_per_week = models.PositiveIntegerField(default=40)
    cost_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))  # per hour
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resource_profiles',
    )
    skills = models.ManyToManyField(Skill, blank=True, related_name='resources')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Allocation(models.Model):
    """A resource's allocation to a project over a time window."""

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='resources_allocations')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='allocations')
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resource_allocations',
    )
    allocation_percent = models.PositiveSmallIntegerField(default=100)
    allocated_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='planned')
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', 'id']

    def __str__(self):
        return f'{self.resource} @ {self.allocation_percent}%'

    @property
    def is_overallocated(self):
        return self.allocation_percent > 100


class TeamAssignment(models.Model):
    """A resource's role on a project team."""

    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('active', 'Active'),
        ('released', 'Released'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='resources_team_assignments')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='assignments')
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='team_assignments',
    )
    role_on_project = models.CharField(max_length=120)
    is_lead = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.resource} — {self.role_on_project}'


class DemandForecast(models.Model):
    """A projected demand vs. capacity forecast for a skill/project period."""

    STATUS_CHOICES = [
        ('projected', 'Projected'),
        ('confirmed', 'Confirmed'),
        ('closed', 'Closed'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='resources_demand_forecasts')
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='demand_forecasts',
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='demand_forecasts',
    )
    period = models.CharField(max_length=10)  # e.g. 2026-07
    demand_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    capacity_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='projected')
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['period', 'id']

    def __str__(self):
        return f'{self.title} ({self.period})'

    @property
    def gap_hours(self):
        return self.demand_hours - self.capacity_hours


class TimeEntry(models.Model):
    """A logged time entry / timesheet line for a resource."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='resources_time_entries')
    number = models.CharField(max_length=20, unique=True, blank=True)  # TE-00001
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='time_entries')
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resource_time_entries',
    )
    work_date = models.DateField(default=timezone.now)
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))
    is_billable = models.BooleanField(default=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-work_date', 'id']

    def __str__(self):
        return f'{self.number} — {self.resource}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = TimeEntry.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'TE-{seq:05d}'
        while TimeEntry.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'TE-{seq:05d}'
        return candidate
