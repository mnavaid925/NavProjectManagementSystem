from django.contrib import admin

from .models import (
    ActivityEntry,
    Channel,
    Meeting,
    Notification,
    SharedDocument,
)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel_type', 'project', 'member_count',
                    'is_archived', 'created_by', 'tenant', 'created_at')
    list_filter = ('channel_type', 'is_archived', 'tenant')
    search_fields = ('name', 'topic', 'description')


@admin.register(SharedDocument)
class SharedDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'doc_type', 'visibility', 'version', 'is_locked',
                    'shared_by', 'tenant', 'created_at')
    list_filter = ('doc_type', 'visibility', 'is_locked', 'tenant')
    search_fields = ('title', 'description')


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'meeting_type', 'scheduled_for',
                    'status', 'organizer', 'tenant', 'created_at')
    list_filter = ('status', 'meeting_type', 'tenant')
    search_fields = ('number', 'title', 'location')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'priority', 'recipient',
                    'is_read', 'tenant', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'tenant')
    search_fields = ('title', 'message')


@admin.register(ActivityEntry)
class ActivityEntryAdmin(admin.ModelAdmin):
    list_display = ('actor', 'verb', 'activity_type', 'entity', 'project',
                    'occurred_at', 'tenant', 'created_at')
    list_filter = ('activity_type', 'tenant')
    search_fields = ('verb', 'entity', 'description')
