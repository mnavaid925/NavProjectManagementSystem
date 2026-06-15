"""System Administration & Security models (tenant-scoped).

Covers the administration phase: security policies, compliance items,
backup jobs, system health metrics, and periodic access reviews.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class SecurityPolicy(models.Model):
    """A security policy with enforcement level, auto-number SEC-00001."""

    POLICY_TYPE_CHOICES = [
        ('password', 'Password'),
        ('mfa', 'MFA'),
        ('session', 'Session'),
        ('ip_allowlist', 'IP Allowlist'),
        ('data_retention', 'Data Retention'),
        ('encryption', 'Encryption'),
    ]
    ENFORCEMENT_LEVEL_CHOICES = [
        ('advisory', 'Advisory'),
        ('enforced', 'Enforced'),
        ('strict', 'Strict'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('retired', 'Retired'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='administration_security_policies',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    policy_type = models.CharField(
        max_length=16, choices=POLICY_TYPE_CHOICES, default='password',
    )
    description = models.TextField(blank=True)
    enforcement_level = models.CharField(
        max_length=10, choices=ENFORCEMENT_LEVEL_CHOICES, default='enforced',
    )
    last_reviewed = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
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
        last = SecurityPolicy.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SEC-{seq:05d}'
        while SecurityPolicy.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SEC-{seq:05d}'
        return candidate


class ComplianceItem(models.Model):
    """A compliance control item against a framework, auto-number CMP-00001."""

    FRAMEWORK_CHOICES = [
        ('soc2', 'SOC 2'),
        ('iso27001', 'ISO 27001'),
        ('gdpr', 'GDPR'),
        ('hipaa', 'HIPAA'),
        ('pci_dss', 'PCI DSS'),
    ]
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='administration_compliance_items',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    framework = models.CharField(max_length=12, choices=FRAMEWORK_CHOICES, default='soc2')
    control_id = models.CharField(max_length=40)
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='administration_complianceitem_owner',
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=14, choices=STATUS_CHOICES, default='not_started')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.control_id}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = ComplianceItem.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CMP-{seq:05d}'
        while ComplianceItem.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CMP-{seq:05d}'
        return candidate


class BackupJob(models.Model):
    """A scheduled backup job with retention, auto-number BK-00001."""

    BACKUP_TYPE_CHOICES = [
        ('full', 'Full'),
        ('incremental', 'Incremental'),
        ('differential', 'Differential'),
        ('snapshot', 'Snapshot'),
    ]
    SCHEDULE_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='administration_backup_jobs',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    backup_type = models.CharField(max_length=14, choices=BACKUP_TYPE_CHOICES, default='full')
    schedule = models.CharField(max_length=10, choices=SCHEDULE_CHOICES, default='daily')
    destination = models.CharField(max_length=200, blank=True)
    size_mb = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_run_at = models.DateTimeField(null=True, blank=True)
    retention_days = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
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
        last = BackupJob.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'BK-{seq:05d}'
        while BackupJob.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'BK-{seq:05d}'
        return candidate


class SystemHealthMetric(models.Model):
    """A recorded system health metric reading, auto-number HM-00001."""

    CATEGORY_CHOICES = [
        ('cpu', 'CPU'),
        ('memory', 'Memory'),
        ('storage', 'Storage'),
        ('api_latency', 'API Latency'),
        ('uptime', 'Uptime'),
        ('queue', 'Queue'),
    ]
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='administration_system_health_metrics',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    metric_name = models.CharField(max_length=120)
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='cpu')
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, blank=True)
    threshold = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    recorded_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='healthy')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.metric_name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = SystemHealthMetric.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'HM-{seq:05d}'
        while SystemHealthMetric.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'HM-{seq:05d}'
        return candidate


class AccessReview(models.Model):
    """A periodic user-access review, auto-number AR-00001."""

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='administration_access_reviews',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=200)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='administration_accessreview_reviewer',
    )
    scope = models.CharField(max_length=120, blank=True)
    users_reviewed = models.PositiveIntegerField(default=0)
    findings = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='scheduled')
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
        last = AccessReview.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'AR-{seq:05d}'
        while AccessReview.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'AR-{seq:05d}'
        return candidate
