"""Quality Management models (tenant-scoped).

Covers quality standards, audits, inspections, continuous-improvement actions,
and deliverable sign-offs. QualityStandard is defined first so the same-app
QualityAudit.standard FK can reference it.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]


class QualityStandard(models.Model):
    """A quality standard / acceptance criterion the project is held to."""

    CATEGORY_CHOICES = [
        ('process', 'Process'),
        ('product', 'Product'),
        ('regulatory', 'Regulatory'),
        ('industry', 'Industry'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('retired', 'Retired'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='quality_standards',
    )
    code = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_standards',
    )
    description = models.TextField(blank=True)
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='process')
    acceptance_criteria = models.TextField(blank=True)
    version = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_standards',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'id']

    def __str__(self):
        return f'{self.code} {self.name}'.strip()


class QualityAudit(models.Model):
    """A quality audit against a standard, with auto-number QA-00001."""

    TYPE_CHOICES = [
        ('process', 'Process'),
        ('compliance', 'Compliance'),
        ('internal', 'Internal'),
        ('external', 'External'),
    ]
    RESULT_CHOICES = [
        ('pass', 'Pass'),
        ('conditional', 'Conditional'),
        ('fail', 'Fail'),
    ]
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='quality_audits',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_audits',
    )
    standard = models.ForeignKey(
        QualityStandard, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audits',
    )
    audit_date = models.DateField(default=timezone.now)
    auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_audits',
    )
    audit_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='process')
    findings_count = models.PositiveIntegerField(default=0)
    result = models.CharField(max_length=12, choices=RESULT_CHOICES, default='pass')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-audit_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = QualityAudit.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'QA-{seq:05d}'
        while QualityAudit.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'QA-{seq:05d}'
        return candidate


class Inspection(models.Model):
    """A quality-control inspection of a deliverable, with auto-number QC-00001."""

    RESULT_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('rework', 'Rework'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='quality_inspections',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_inspections',
    )
    inspection_date = models.DateField(default=timezone.now)
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_inspections',
    )
    deliverable = models.CharField(max_length=160, blank=True)
    defects_found = models.PositiveIntegerField(default=0)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pass')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-inspection_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Inspection.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'QC-{seq:05d}'
        while Inspection.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'QC-{seq:05d}'
        return candidate


class ImprovementAction(models.Model):
    """A continuous-improvement / corrective action, with auto-number CI-00001."""

    SOURCE_CHOICES = [
        ('audit', 'Audit'),
        ('inspection', 'Inspection'),
        ('retrospective', 'Retrospective'),
        ('feedback', 'Feedback'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='quality_improvements',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_improvements',
    )
    description = models.TextField(blank=True)
    source = models.CharField(max_length=14, choices=SOURCE_CHOICES, default='audit')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_improvements',
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
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
        last = ImprovementAction.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CI-{seq:05d}'
        while ImprovementAction.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CI-{seq:05d}'
        return candidate


class DeliverableSignoff(models.Model):
    """A deliverable sign-off / approval record, with auto-number SO-00001."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revisions', 'Revisions Requested'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='quality_signoffs',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    deliverable_name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_signoffs',
    )
    description = models.TextField(blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_signoffs_submitted',
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quality_signoffs_approved',
    )
    submitted_date = models.DateField(default=timezone.now)
    signoff_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.deliverable_name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = DeliverableSignoff.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SO-{seq:05d}'
        while DeliverableSignoff.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SO-{seq:05d}'
        return candidate
