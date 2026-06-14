"""Core models: timestamp base, Tenant, tenant-scoped base, and audit log."""
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base adding created/updated timestamps to any model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Tenant(TimeStampedModel):
    """An organization (customer) in the multi-tenant system."""

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=80, unique=True)
    subdomain = models.CharField(max_length=80, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_tenants',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TenantScopedModel(TimeStampedModel):
    """Abstract base for every model that belongs to exactly one tenant."""

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
    )

    class Meta:
        abstract = True


class AuditLog(TimeStampedModel):
    """Immutable record of meaningful actions for forensic search."""

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=80)
    entity = models.CharField(max_length=120)
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} {self.entity} ({self.created_at:%Y-%m-%d %H:%M})'
