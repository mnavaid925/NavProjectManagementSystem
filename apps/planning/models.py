"""Project Planning & Scheduling models (tenant-scoped).

Covers WBS work packages, schedule tasks, task dependencies, milestones /
phase gates, and schedule baselines. Every model is tenant-scoped per the
multi-tenancy rules.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models


class WorkPackage(models.Model):
    """A WBS work package (optionally nested via a self parent)."""

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='planning_work_packages',
    )
    code = models.CharField(max_length=40, blank=True)  # WBS code e.g. "1.2.3"
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='work_packages',
    )
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='children',
    )
    description = models.TextField(blank=True)
    level = models.PositiveSmallIntegerField(default=1)
    estimated_effort_hours = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='work_packages',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='not_started')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code', 'id']

    def __str__(self):
        return f'{self.code} {self.name}'.strip()


class ScheduleTask(models.Model):
    """A schedulable task with duration & effort estimation."""

    ESTIMATE_METHOD_CHOICES = [
        ('analogous', 'Analogous'),
        ('parametric', 'Parametric'),
        ('bottom_up', 'Bottom-Up'),
        ('three_point', 'Three-Point'),
    ]
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='planning_schedule_tasks',
    )
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='schedule_tasks',
    )
    work_package = models.ForeignKey(
        WorkPackage, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='schedule_tasks',
    )
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='schedule_tasks',
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration_days = models.PositiveIntegerField(default=1)
    effort_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    estimate_method = models.CharField(
        max_length=14, choices=ESTIMATE_METHOD_CHOICES, default='bottom_up',
    )
    percent_complete = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='not_started')
    is_critical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'id']

    def __str__(self):
        return self.name


class TaskDependency(models.Model):
    """A precedence link between two schedule tasks."""

    DEPENDENCY_TYPE_CHOICES = [
        ('FS', 'Finish-to-Start'),
        ('SS', 'Start-to-Start'),
        ('FF', 'Finish-to-Finish'),
        ('SF', 'Start-to-Finish'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='planning_task_dependencies',
    )
    predecessor = models.ForeignKey(
        ScheduleTask, on_delete=models.CASCADE, related_name='successor_links',
    )
    successor = models.ForeignKey(
        ScheduleTask, on_delete=models.CASCADE, related_name='predecessor_links',
    )
    dependency_type = models.CharField(
        max_length=2, choices=DEPENDENCY_TYPE_CHOICES, default='FS',
    )
    lag_days = models.IntegerField(default=0)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.predecessor} → {self.successor} ({self.dependency_type})'


class Milestone(models.Model):
    """A schedule milestone or phase gate."""

    MILESTONE_TYPE_CHOICES = [
        ('milestone', 'Milestone'),
        ('phase_gate', 'Phase Gate'),
    ]
    GATE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='planning_milestones',
    )
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='planning_milestones',
    )
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    milestone_type = models.CharField(
        max_length=12, choices=MILESTONE_TYPE_CHOICES, default='milestone',
    )
    gate_status = models.CharField(
        max_length=10, choices=GATE_STATUS_CHOICES, default='pending',
    )
    entry_criteria = models.TextField(blank=True)
    exit_criteria = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'id']

    def __str__(self):
        return self.name


class ScheduleBaseline(models.Model):
    """A saved schedule baseline / version for a project."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='planning_schedule_baselines',
    )
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='schedule_baselines',
    )
    version = models.CharField(max_length=20, blank=True)  # e.g. v1.0
    baseline_date = models.DateField(null=True, blank=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_finish = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    is_current = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-baseline_date', 'id']

    def __str__(self):
        return f'{self.name} {self.version}'.strip()
