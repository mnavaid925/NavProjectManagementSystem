"""Risk & Issue Management models (tenant-scoped).

Covers the risk register, qualitative/quantitative risk analysis, risk
response planning, the issue log, and periodic risk reviews.
"""
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

LEVEL_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

# Maps the qualitative low/medium/high scale to an integer weight 1..3 so a
# risk score can be computed as probability * impact (range 1..9).
LEVEL_SCORE = {'low': 1, 'medium': 2, 'high': 3}


class Risk(models.Model):
    """A risk in the project risk register, with auto-number RSK-00001."""

    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('external', 'External'),
        ('organizational', 'Organizational'),
        ('pm', 'Project Mgmt'),
        ('financial', 'Financial'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('mitigating', 'Mitigating'),
        ('closed', 'Closed'),
        ('occurred', 'Occurred'),
    ]
    LEVEL_CHOICES = LEVEL_CHOICES

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='risks_risks',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks_risks',
    )
    description = models.TextField(blank=True)
    category = models.CharField(max_length=14, choices=CATEGORY_CHOICES, default='technical')
    probability = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='medium')
    impact = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='medium')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks_risks_owned',
    )
    identified_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.title}'

    @property
    def risk_score(self):
        """Probability x impact on the 1..3 scale → integer 1..9."""
        return LEVEL_SCORE.get(self.probability, 0) * LEVEL_SCORE.get(self.impact, 0)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Risk.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'RSK-{seq:05d}'
        while Risk.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'RSK-{seq:05d}'
        return candidate


class RiskAnalysis(models.Model):
    """A qualitative or quantitative analysis of a single risk."""

    TYPE_CHOICES = [
        ('qualitative', 'Qualitative'),
        ('quantitative', 'Quantitative'),
    ]
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='risks_analyses',
    )
    risk = models.ForeignKey(
        Risk, on_delete=models.CASCADE, related_name='analyses',
    )
    analysis_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='qualitative')
    probability_pct = models.PositiveSmallIntegerField(default=0)
    impact_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='medium')
    notes = models.TextField(blank=True)
    analyzed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks_analyses',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.risk} — {self.get_analysis_type_display()}'

    @property
    def emv(self):
        """Expected Monetary Value = probability fraction x impact cost."""
        return (Decimal(self.probability_pct) / Decimal('100') * self.impact_cost).quantize(Decimal('0.01'))


class RiskResponse(models.Model):
    """A planned response (strategy + action) for a risk."""

    STRATEGY_CHOICES = [
        ('avoid', 'Avoid'),
        ('transfer', 'Transfer'),
        ('mitigate', 'Mitigate'),
        ('accept', 'Accept'),
        ('escalate', 'Escalate'),
    ]
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='risks_responses',
    )
    risk = models.ForeignKey(
        Risk, on_delete=models.CASCADE, related_name='responses',
    )
    strategy = models.CharField(max_length=10, choices=STRATEGY_CHOICES, default='mitigate')
    description = models.TextField(blank=True)
    action_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks_responses',
    )
    planned_action = models.CharField(max_length=200, blank=True)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    trigger_condition = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_strategy_display()} for {self.risk}'


class Issue(models.Model):
    """An issue in the issue log, with auto-number ISS-00001."""

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('escalated', 'Escalated'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='risks_issues',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks_issues',
    )
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks_issues',
    )
    raised_date = models.DateField(default=timezone.now)
    resolved_date = models.DateField(null=True, blank=True)
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
        last = Issue.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'ISS-{seq:05d}'
        while Issue.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'ISS-{seq:05d}'
        return candidate


class RiskReview(models.Model):
    """A periodic risk review meeting record."""

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='risks_reviews',
    )
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks_reviews',
    )
    review_date = models.DateField(default=timezone.now)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='risks_reviews',
    )
    summary = models.TextField(blank=True)
    risks_reviewed = models.PositiveIntegerField(default=0)
    top_risk = models.ForeignKey(
        Risk, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='top_in_reviews',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-review_date', '-id']

    def __str__(self):
        return self.title
