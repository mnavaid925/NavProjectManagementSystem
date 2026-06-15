from django.contrib import admin

from .models import (
    AccessReview,
    BackupJob,
    ComplianceItem,
    SecurityPolicy,
    SystemHealthMetric,
)


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'policy_type', 'enforcement_level',
                    'last_reviewed', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'policy_type', 'tenant')
    search_fields = ('number', 'name', 'description')


@admin.register(ComplianceItem)
class ComplianceItemAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'framework', 'control_id', 'owner',
                    'due_date', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'framework', 'tenant')
    search_fields = ('number', 'title', 'control_id')


@admin.register(BackupJob)
class BackupJobAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'backup_type', 'schedule', 'destination',
                    'size_mb', 'last_run_at', 'retention_days', 'status', 'tenant')
    list_filter = ('status', 'backup_type', 'tenant')
    search_fields = ('number', 'name', 'destination')


@admin.register(SystemHealthMetric)
class SystemHealthMetricAdmin(admin.ModelAdmin):
    list_display = ('number', 'metric_name', 'category', 'value', 'unit',
                    'threshold', 'recorded_at', 'status', 'tenant')
    list_filter = ('status', 'category', 'tenant')
    search_fields = ('number', 'metric_name', 'unit')


@admin.register(AccessReview)
class AccessReviewAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'reviewer', 'scope', 'users_reviewed',
                    'due_date', 'completed_date', 'status', 'tenant')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'title', 'scope')
