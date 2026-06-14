"""Collaboration & Communication models (tenant-scoped).

Covers team collaboration: channels, shared documents, meetings (with
auto-numbered MTG codes), notifications, and an activity feed. Every model is
scoped to a tenant and carries created/updated timestamps.
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


class Channel(models.Model):
    """A team communication channel (public/private/direct/announcement)."""

    CHANNEL_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('direct', 'Direct Message'),
        ('announcement', 'Announcement'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='collab_channels',
    )
    name = models.CharField(max_length=120)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_channels',
    )
    channel_type = models.CharField(max_length=16, choices=CHANNEL_TYPE_CHOICES, default='public')
    topic = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    member_count = models.PositiveSmallIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_channels',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SharedDocument(models.Model):
    """A shared/linked document with type, visibility, version, and lock state."""

    DOC_TYPE_CHOICES = [
        ('doc', 'Document'),
        ('sheet', 'Spreadsheet'),
        ('slide', 'Presentation'),
        ('pdf', 'PDF'),
        ('other', 'Other'),
    ]
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('team', 'Team'),
        ('public', 'Public'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='collab_shared_documents',
    )
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_shared_documents',
    )
    doc_type = models.CharField(max_length=12, choices=DOC_TYPE_CHOICES, default='doc')
    doc_url = models.URLField(blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='team')
    version = models.CharField(max_length=20, blank=True, default='1.0')
    is_locked = models.BooleanField(default=False)
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_shared_documents',
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Meeting(models.Model):
    """A scheduled meeting with agenda/minutes, auto-number MTG-00001."""

    MEETING_TYPE_CHOICES = [
        ('standup', 'Standup'),
        ('review', 'Review'),
        ('planning', 'Planning'),
        ('client', 'Client'),
        ('retro', 'Retrospective'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='collab_meetings',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_meetings',
    )
    meeting_type = models.CharField(max_length=12, choices=MEETING_TYPE_CHOICES, default='standup')
    scheduled_for = models.DateTimeField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField(default=30)
    location = models.CharField(max_length=160, blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_meetings',
    )
    agenda = models.TextField(blank=True)
    minutes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_for', '-id']

    def __str__(self):
        return f'{self.number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Meeting.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'MTG-{seq:05d}'
        while Meeting.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'MTG-{seq:05d}'
        return candidate


class Notification(models.Model):
    """A user-facing notification with type/priority/read state."""

    TYPE_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('alert', 'Alert'),
    ]
    PRIORITY_CHOICES = PRIORITY_CHOICES

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='collab_notifications',
    )
    title = models.CharField(max_length=160)
    message = models.TextField(blank=True)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_notifications',
    )
    notification_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ActivityEntry(models.Model):
    """A single entry in the activity feed (actor + verb + entity)."""

    TYPE_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('comment', 'Comment'),
        ('status', 'Status Change'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='collab_activities',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_activities',
    )
    verb = models.CharField(max_length=80)
    activity_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='create')
    entity = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='collab_activities',
    )
    occurred_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-occurred_at', '-id']

    def __str__(self):
        actor = self.actor.get_full_name() if self.actor else 'Someone'
        return f'{actor} {self.verb} {self.entity}'
