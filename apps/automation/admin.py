from django.contrib import admin

from .models import (
    ApprovalRule,
    AutomationHook,
    NotificationRule,
    RecurringRule,
    WorkflowDefinition,
)


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'trigger_event', 'entity_type', 'project',
                    'owner', 'step_count', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'trigger_event', 'tenant')
    search_fields = ('number', 'name', 'entity_type')


@admin.register(ApprovalRule)
class ApprovalRuleAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'entity_type', 'threshold_amount', 'approver',
                    'escalation_hours', 'auto_approve_below', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'name', 'entity_type')


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'trigger_event', 'channel', 'lead_time_hours',
                    'recipient_role', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'channel', 'tenant')
    search_fields = ('number', 'name', 'recipient_role')


@admin.register(RecurringRule)
class RecurringRuleAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'frequency', 'project', 'assignee',
                    'next_run_date', 'task_template', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'frequency', 'tenant')
    search_fields = ('number', 'name', 'task_template')


@admin.register(AutomationHook)
class AutomationHookAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'hook_type', 'target_url', 'event',
                    'status', 'tenant', 'created_at')
    list_filter = ('status', 'hook_type', 'tenant')
    search_fields = ('number', 'name', 'event')
