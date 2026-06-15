from django.contrib import admin

from .models import (
    ApiKey,
    Connector,
    SyncJob,
    SyncLog,
    Webhook,
)


@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'category', 'provider', 'auth_type',
                    'status', 'owner', 'last_sync_at', 'tenant', 'created_at')
    list_filter = ('status', 'category', 'auth_type', 'tenant')
    search_fields = ('number', 'name', 'provider', 'base_url')


@admin.register(SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'connector', 'direction', 'schedule',
                    'records_synced', 'status', 'last_run_at', 'tenant', 'created_at')
    list_filter = ('status', 'direction', 'schedule', 'tenant')
    search_fields = ('number', 'name')


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('number', 'connector', 'sync_job', 'level', 'status',
                    'records_processed', 'logged_at', 'tenant', 'created_at')
    list_filter = ('status', 'level', 'tenant')
    search_fields = ('number', 'message')


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    # WARNING: do not add the raw secret to list_display/search_fields - never render or log it.
    list_display = ('number', 'name', 'target_url', 'event', 'status',
                    'last_triggered_at', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'name', 'event')


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    # WARNING: hashed_key must never be shown in admin - exclude it from list_display/search_fields.
    list_display = ('number', 'name', 'key_prefix', 'scopes', 'status',
                    'owner', 'expires_at', 'last_used_at', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'name', 'scopes')
