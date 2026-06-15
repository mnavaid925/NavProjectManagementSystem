"""Integration & API Hub models (tenant-scoped).

Covers the integration phase: external connectors, scheduled sync jobs, sync
log entries, outbound webhooks, and API keys. Connectors are the root entity;
sync jobs and logs reference connectors, and logs also reference sync jobs.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Connector(models.Model):
    """An external system connector, auto-number CON-00001."""

    CATEGORY_CHOICES = [
        ('erp', 'ERP & Financial'),
        ('crm', 'CRM'),
        ('hr', 'HR & Talent'),
        ('devops', 'Development & DevOps'),
        ('storage', 'File Storage'),
    ]
    AUTH_TYPE_CHOICES = [
        ('oauth2', 'OAuth 2.0'),
        ('api_key', 'API Key'),
        ('basic', 'Basic Auth'),
        ('token', 'Token'),
    ]
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
        ('pending', 'Pending'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='integrations_connectors',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='erp')
    provider = models.CharField(max_length=80)
    auth_type = models.CharField(max_length=10, choices=AUTH_TYPE_CHOICES, default='oauth2')
    base_url = models.URLField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='integrations_connector_owner',
    )
    last_sync_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
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
        last = Connector.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CON-{seq:05d}'
        while Connector.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CON-{seq:05d}'
        return candidate


class SyncJob(models.Model):
    """A scheduled data sync job for a connector, auto-number SJ-00001."""

    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
        ('bidirectional', 'Bidirectional'),
    ]
    SCHEDULE_CHOICES = [
        ('manual', 'Manual'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    STATUS_CHOICES = [
        ('idle', 'Idle'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='integrations_sync_jobs',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    connector = models.ForeignKey(
        Connector, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='integrations_syncjob_connector',
    )
    direction = models.CharField(max_length=14, choices=DIRECTION_CHOICES, default='inbound')
    schedule = models.CharField(max_length=10, choices=SCHEDULE_CHOICES, default='daily')
    records_synced = models.PositiveIntegerField(default=0)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='idle')
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
        last = SyncJob.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SJ-{seq:05d}'
        while SyncJob.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SJ-{seq:05d}'
        return candidate


class SyncLog(models.Model):
    """A sync log entry for a connector/sync job, auto-number SL-00001."""

    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='integrations_sync_logs',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    connector = models.ForeignKey(
        Connector, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='integrations_synclog_connector',
    )
    sync_job = models.ForeignKey(
        SyncJob, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='integrations_synclog_sync_job',
    )
    level = models.CharField(max_length=8, choices=LEVEL_CHOICES, default='info')
    message = models.TextField(blank=True)
    records_processed = models.PositiveIntegerField(default=0)
    logged_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='success')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.level}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = SyncLog.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SL-{seq:05d}'
        while SyncLog.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SL-{seq:05d}'
        return candidate


class Webhook(models.Model):
    """An outbound webhook subscription, auto-number WH-00001."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='integrations_webhooks',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    target_url = models.URLField()
    event = models.CharField(max_length=80, blank=True)
    # WARNING: storing the secret as plaintext is insecure - encrypt at rest or store only a reference; never log or render the raw secret.
    secret = models.CharField(max_length=128, blank=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
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
        last = Webhook.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'WH-{seq:05d}'
        while Webhook.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'WH-{seq:05d}'
        return candidate


class ApiKey(models.Model):
    """An API key with a one-way hashed secret, auto-number AK-00001."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='integrations_api_keys',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    key_prefix = models.CharField(max_length=16, blank=True)
    # WARNING: never persist the raw API key - store only a one-way hash plus a short displayable prefix. Exclude hashed_key from the ModelForm and never render it or any raw key in templates.
    hashed_key = models.CharField(max_length=128, blank=True)
    scopes = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='integrations_apikey_owner',
    )
    expires_at = models.DateField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
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
        last = ApiKey.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'AK-{seq:05d}'
        while ApiKey.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'AK-{seq:05d}'
        return candidate
