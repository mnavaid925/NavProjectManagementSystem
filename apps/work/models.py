"""Task & Work Management models (tenant-scoped).

Covers the agile delivery layer: work items (tasks/bugs/stories) with an
auto-number WRK-#####, prioritisation scores (WSJF/RICE/MoSCoW/Eisenhower),
kanban board columns and cards, and work-item dependencies.
"""
from decimal import Decimal  # noqa: F401  (kept for convention parity across modules)

from django.conf import settings
from django.db import models
from django.utils import timezone  # noqa: F401  (kept for convention parity across modules)

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]


class WorkItem(models.Model):
    """A single unit of work (task/bug/story/spike/chore), auto-number WRK-00001."""

    ITEM_TYPE_CHOICES = [
        ('task', 'Task'),
        ('bug', 'Bug'),
        ('story', 'Story'),
        ('spike', 'Spike'),
        ('chore', 'Chore'),
    ]
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='work_items',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='work_items',
    )
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=16, choices=ITEM_TYPE_CHOICES, default='task')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_work_items',
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reported_work_items',
    )
    story_points = models.PositiveSmallIntegerField(null=True, blank=True)
    estimate_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = WorkItem.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'WRK-{seq:05d}'
        while WorkItem.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'WRK-{seq:05d}'
        return candidate


class PriorityScore(models.Model):
    """A prioritisation score for a work item (WSJF/RICE/MoSCoW/Eisenhower)."""

    METHOD_CHOICES = [
        ('moscow', 'MoSCoW'),
        ('wsjf', 'WSJF'),
        ('rice', 'RICE'),
        ('eisenhower', 'Eisenhower'),
    ]
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='work_priority_scores',
    )
    work_item = models.ForeignKey(
        WorkItem, on_delete=models.CASCADE, related_name='priority_scores',
    )
    method = models.CharField(max_length=16, choices=METHOD_CHOICES, default='wsjf')
    urgency = models.CharField(max_length=12, choices=URGENCY_CHOICES, default='medium')
    business_value = models.PositiveSmallIntegerField(default=0)
    effort = models.PositiveSmallIntegerField(default=0)
    score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    rationale = models.TextField(blank=True)
    scored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='work_priority_scores',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-score', '-id']

    def __str__(self):
        return f'{self.work_item} — {self.get_method_display()}'


class BoardColumn(models.Model):
    """A kanban board column (backlog/todo/in_progress/review/done)."""

    COLUMN_TYPE_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='work_board_columns',
    )
    name = models.CharField(max_length=80)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='work_board_columns',
    )
    column_type = models.CharField(max_length=16, choices=COLUMN_TYPE_CHOICES, default='todo')
    order = models.PositiveSmallIntegerField(default=0)
    wip_limit = models.PositiveSmallIntegerField(default=0)
    is_done_column = models.BooleanField(default=False)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class BoardCard(models.Model):
    """A kanban card placed in a board column, optionally linked to a work item."""

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='work_board_cards',
    )
    title = models.CharField(max_length=160)
    work_item = models.ForeignKey(
        WorkItem, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='board_cards',
    )
    column = models.ForeignKey(
        BoardColumn, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cards',
    )
    position = models.PositiveSmallIntegerField(default=0)
    planned_start = models.DateField(null=True, blank=True)
    planned_end = models.DateField(null=True, blank=True)
    progress = models.PositiveSmallIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    color = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['column', 'position', 'id']

    def __str__(self):
        return self.title


class WorkDependency(models.Model):
    """A dependency relationship between two work items."""

    DEP_TYPE_CHOICES = [
        ('finish_to_start', 'Finish to Start'),
        ('start_to_start', 'Start to Start'),
        ('finish_to_finish', 'Finish to Finish'),
        ('start_to_finish', 'Start to Finish'),
        ('blocks', 'Blocks'),
        ('relates', 'Relates To'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='work_dependencies',
    )
    work_item = models.ForeignKey(
        WorkItem, on_delete=models.CASCADE, related_name='dependencies',
    )
    depends_on = models.ForeignKey(
        WorkItem, on_delete=models.CASCADE, related_name='dependents',
    )
    dependency_type = models.CharField(
        max_length=20, choices=DEP_TYPE_CHOICES, default='finish_to_start',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    lag_days = models.IntegerField(default=0)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.work_item} → {self.depends_on}'
