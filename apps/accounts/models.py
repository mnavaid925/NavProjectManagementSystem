"""Accounts models: custom User, Role, UserInvite, UserPreference."""
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user belonging to (at most) one tenant."""

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    phone = models.CharField(max_length=40, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_tenant_admin = models.BooleanField(default=False)
    role = models.ForeignKey(
        'accounts.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
    )

    class Meta:
        ordering = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        first = (self.first_name or self.username or '?')[:1]
        last = (self.last_name or '')[:1]
        return (first + last).upper()


class Role(models.Model):
    """A named permission set scoped to a tenant (or system-wide)."""

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='roles',
    )
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list, blank=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('tenant', 'name')

    def __str__(self):
        return self.name


class UserInvite(models.Model):
    """An invitation to join a tenant, redeemable via a unique token."""

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_EXPIRED = 'expired'
    STATUS_REVOKED = 'revoked'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_REVOKED, 'Revoked'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='invites',
    )
    email = models.EmailField()
    role = models.ForeignKey(
        'accounts.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invites',
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    invited_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_invites',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    message = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} -> {self.tenant} ({self.status})'

    def is_expired(self):
        return timezone.now() >= self.expires_at


class UserPreference(models.Model):
    """Per-user UI/theme preferences mirrored to body data-* attributes."""

    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark')]
    LAYOUT_CHOICES = [
        ('vertical', 'Vertical'),
        ('horizontal', 'Horizontal'),
        ('detached', 'Detached'),
    ]
    SIDEBAR_SIZE_CHOICES = [
        ('default', 'Default'),
        ('compact', 'Compact'),
        ('small-icon', 'Small Icon'),
        ('icon-hover', 'Icon Hover'),
    ]
    SIDEBAR_COLOR_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('brand', 'Brand'),
    ]
    TOPBAR_CHOICES = [('light', 'Light'), ('dark', 'Dark')]
    WIDTH_CHOICES = [('fluid', 'Fluid'), ('boxed', 'Boxed')]
    POSITION_CHOICES = [('fixed', 'Fixed'), ('scrollable', 'Scrollable')]
    DIRECTION_CHOICES = [('ltr', 'LTR'), ('rtl', 'RTL')]

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='preference',
    )
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    layout = models.CharField(max_length=12, choices=LAYOUT_CHOICES, default='vertical')
    sidebar_size = models.CharField(max_length=12, choices=SIDEBAR_SIZE_CHOICES, default='default')
    sidebar_color = models.CharField(max_length=10, choices=SIDEBAR_COLOR_CHOICES, default='light')
    topbar = models.CharField(max_length=10, choices=TOPBAR_CHOICES, default='light')
    width = models.CharField(max_length=10, choices=WIDTH_CHOICES, default='fluid')
    position = models.CharField(max_length=12, choices=POSITION_CHOICES, default='fixed')
    direction = models.CharField(max_length=5, choices=DIRECTION_CHOICES, default='ltr')
    preloader = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Preferences for {self.user}'
