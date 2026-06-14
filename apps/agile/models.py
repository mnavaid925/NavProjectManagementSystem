"""Agile & Scrum Management models (tenant-scoped).

Covers the agile delivery phase: epics, sprints, a product backlog of items
(stories/bugs/tasks/spikes), releases, and sprint retrospectives.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]


class Epic(models.Model):
    """A large body of work broken into backlog items, auto-number EPIC-00001."""

    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='agile_epics',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_epics',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_epics',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='proposed')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    business_value = models.IntegerField(default=0)
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
        last = Epic.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'EPIC-{seq:05d}'
        while Epic.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'EPIC-{seq:05d}'
        return candidate


class Sprint(models.Model):
    """A time-boxed iteration with capacity/commitment tracking, auto-number SPR-00001."""

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='agile_sprints',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_sprints',
    )
    goal = models.CharField(max_length=240, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='planned')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    capacity_points = models.IntegerField(default=0)
    committed_points = models.IntegerField(default=0)
    completed_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Sprint.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SPR-{seq:05d}'
        while Sprint.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SPR-{seq:05d}'
        return candidate


class BacklogItem(models.Model):
    """A single product backlog item (story/bug/task/spike), auto-number BLI-00001."""

    ITEM_TYPE_CHOICES = [
        ('story', 'Story'),
        ('bug', 'Bug'),
        ('task', 'Task'),
        ('spike', 'Spike'),
    ]
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='agile_backlog_items',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=8, choices=ITEM_TYPE_CHOICES, default='story')
    epic = models.ForeignKey(
        Epic, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_backlog_items',
    )
    sprint = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_backlog_items',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    story_points = models.IntegerField(default=0)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_backlog_items',
    )
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
        last = BacklogItem.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'BLI-{seq:05d}'
        while BacklogItem.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'BLI-{seq:05d}'
        return candidate


class Release(models.Model):
    """A planned product release / version, auto-number REL-00001."""

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('released', 'Released'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='agile_releases',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    version = models.CharField(max_length=40, blank=True)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_releases',
    )
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='planned')
    release_date = models.DateField(null=True, blank=True)
    release_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_releases',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Release.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'REL-{seq:05d}'
        while Release.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'REL-{seq:05d}'
        return candidate


class Retrospective(models.Model):
    """A sprint retrospective capturing what went well / needs improvement, auto-number RETRO-00001."""

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='agile_retrospectives',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    sprint = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_retrospectives',
    )
    title = models.CharField(max_length=160)
    retro_date = models.DateField(default=timezone.now)
    facilitator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agile_retrospectives',
    )
    went_well = models.TextField(blank=True)
    needs_improvement = models.TextField(blank=True)
    action_items = models.TextField(blank=True)
    team_health_score = models.IntegerField(default=3)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-retro_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Retrospective.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'RETRO-{seq:05d}'
        while Retrospective.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'RETRO-{seq:05d}'
        return candidate
