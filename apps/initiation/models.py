"""Project Initiation & Charter models (tenant-scoped).

Covers the initiation phase: intake requests, business cases, project
charters, stakeholder register, and kickoff checklist tasks.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]

LEVEL_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]


class ProjectRequest(models.Model):
    """An intake request to start a project, with auto-number REQ-00001."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='initiation_requests',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    department = models.CharField(max_length=120, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='initiation_requests_made',
    )
    description = models.TextField(blank=True)
    expected_benefit = models.TextField(blank=True)
    estimated_budget = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    target_start_date = models.DateField(null=True, blank=True)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='initiation_requests',
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
        last = ProjectRequest.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'REQ-{seq:05d}'
        while ProjectRequest.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'REQ-{seq:05d}'
        return candidate


class BusinessCase(models.Model):
    """A business case justifying a request, with auto-number BC-00001."""

    RECOMMENDATION_CHOICES = [
        ('go', 'Go'),
        ('no_go', 'No-Go'),
        ('hold', 'Hold'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='initiation_business_cases',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    request = models.ForeignKey(
        ProjectRequest, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='business_cases',
    )
    summary = models.TextField(blank=True)
    problem_statement = models.TextField(blank=True)
    expected_roi = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))
    estimated_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    estimated_benefit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    payback_months = models.PositiveIntegerField(default=0)
    recommendation = models.CharField(max_length=10, choices=RECOMMENDATION_CHOICES, default='go')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.title}'

    @property
    def net_benefit(self):
        return self.estimated_benefit - self.estimated_cost

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = BusinessCase.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'BC-{seq:05d}'
        while BusinessCase.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'BC-{seq:05d}'
        return candidate


class ProjectCharter(models.Model):
    """A project charter authorizing a project, with auto-number CHTR-00001."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='initiation_charters',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='charters',
    )
    sponsor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sponsored_charters',
    )
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managed_charters',
    )
    objectives = models.TextField(blank=True)
    scope_summary = models.TextField(blank=True)
    success_criteria = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    approved_at = models.DateField(null=True, blank=True)
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
        last = ProjectCharter.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CHTR-{seq:05d}'
        while ProjectCharter.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CHTR-{seq:05d}'
        return candidate


class Stakeholder(models.Model):
    """A project stakeholder with influence/interest/engagement ratings."""

    LEVEL_CHOICES = LEVEL_CHOICES
    ENGAGEMENT_CHOICES = [
        ('unaware', 'Unaware'),
        ('resistant', 'Resistant'),
        ('neutral', 'Neutral'),
        ('supportive', 'Supportive'),
        ('leading', 'Leading'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='initiation_stakeholders',
    )
    name = models.CharField(max_length=150)
    organization = models.CharField(max_length=150, blank=True)
    role_title = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='stakeholders',
    )
    influence = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='medium')
    interest = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='medium')
    engagement = models.CharField(max_length=12, choices=ENGAGEMENT_CHOICES, default='neutral')
    communication_preference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class KickoffTask(models.Model):
    """A kickoff checklist task tied to a project/charter."""

    CATEGORY_CHOICES = [
        ('logistics', 'Logistics'),
        ('team', 'Team'),
        ('comms', 'Communications'),
        ('governance', 'Governance'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='initiation_kickoff_tasks',
    )
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='kickoff_tasks',
    )
    charter = models.ForeignKey(
        ProjectCharter, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='kickoff_tasks',
    )
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='kickoff_tasks',
    )
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='logistics')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_complete', 'due_date', 'id']

    def __str__(self):
        return self.title
