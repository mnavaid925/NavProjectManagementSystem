"""Scope & Requirements Management models (tenant-scoped).

Covers the scope/requirements phase: requirements register with MoSCoW
prioritisation, requirement traceability links, scope statements, change
requests, and scope verification records.
"""
from decimal import Decimal  # noqa: F401  (kept for convention parity across modules)

from django.conf import settings
from django.db import models
from django.utils import timezone

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]


class Requirement(models.Model):
    """A single project requirement with type/MoSCoW/status, auto-number RQ-00001."""

    TYPE_CHOICES = [
        ('functional', 'Functional'),
        ('non_functional', 'Non-Functional'),
        ('business', 'Business'),
        ('technical', 'Technical'),
        ('user', 'User'),
    ]
    MOSCOW_CHOICES = [
        ('must', 'Must Have'),
        ('should', 'Should Have'),
        ('could', 'Could Have'),
        ('wont', "Won't Have"),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('implemented', 'Implemented'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='scope_requirements',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scope_requirements',
    )
    description = models.TextField(blank=True)
    requirement_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default='functional')
    moscow = models.CharField(max_length=8, choices=MOSCOW_CHOICES, default='must')
    source = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scope_requirements',
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
        last = Requirement.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'RQ-{seq:05d}'
        while Requirement.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'RQ-{seq:05d}'
        return candidate


class RequirementTrace(models.Model):
    """A traceability link between a requirement and a downstream artifact."""

    TRACE_TYPE_CHOICES = [
        ('forward', 'Forward'),
        ('backward', 'Backward'),
        ('bidirectional', 'Bidirectional'),
    ]
    ARTIFACT_CHOICES = [
        ('design', 'Design'),
        ('test', 'Test'),
        ('code', 'Code'),
        ('deliverable', 'Deliverable'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='scope_traces',
    )
    requirement = models.ForeignKey(
        Requirement, on_delete=models.CASCADE, related_name='traces',
    )
    trace_type = models.CharField(max_length=14, choices=TRACE_TYPE_CHOICES, default='forward')
    linked_artifact = models.CharField(max_length=160)
    artifact_type = models.CharField(max_length=12, choices=ARTIFACT_CHOICES, default='test')
    verified = models.BooleanField(default=False)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.requirement} → {self.linked_artifact}'


class ScopeStatement(models.Model):
    """A project scope statement (in/out of scope, assumptions, etc.), auto-number SCP-00001."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('baselined', 'Baselined'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='scope_statements',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scope_statements',
    )
    in_scope = models.TextField(blank=True)
    out_of_scope = models.TextField(blank=True)
    assumptions = models.TextField(blank=True)
    constraints = models.TextField(blank=True)
    deliverables = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scope_statements',
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
        last = ScopeStatement.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SCP-{seq:05d}'
        while ScopeStatement.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SCP-{seq:05d}'
        return candidate


class ChangeRequest(models.Model):
    """A request to change project scope/requirements, auto-number CR-00001."""

    TYPE_CHOICES = [
        ('add', 'Add'),
        ('modify', 'Modify'),
        ('remove', 'Remove'),
    ]
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='scope_change_requests',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scope_change_requests',
    )
    requirement = models.ForeignKey(
        Requirement, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='change_requests',
    )
    description = models.TextField(blank=True)
    change_type = models.CharField(max_length=8, choices=TYPE_CHOICES, default='modify')
    impact_summary = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=14, choices=STATUS_CHOICES, default='submitted')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scope_change_requests',
    )
    decided_at = models.DateField(null=True, blank=True)
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
        last = ChangeRequest.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CR-{seq:05d}'
        while ChangeRequest.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CR-{seq:05d}'
        return candidate


class ScopeVerification(models.Model):
    """A scope verification / deliverable acceptance record, auto-number SV-00001."""

    RESULT_CHOICES = [
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('conditional', 'Conditional'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='scope_verifications',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scope_verifications',
    )
    scope_statement = models.ForeignKey(
        ScopeStatement, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verifications',
    )
    verification_date = models.DateField(default=timezone.now)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scope_verifications',
    )
    deliverable = models.CharField(max_length=160, blank=True)
    result = models.CharField(max_length=12, choices=RESULT_CHOICES, default='accepted')
    scope_creep_flag = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-verification_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = ScopeVerification.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SV-{seq:05d}'
        while ScopeVerification.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SV-{seq:05d}'
        return candidate
