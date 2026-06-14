from django.contrib import admin

from .models import (
    BusinessCase,
    KickoffTask,
    ProjectCharter,
    ProjectRequest,
    Stakeholder,
)


@admin.register(ProjectRequest)
class ProjectRequestAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'department', 'priority', 'status',
                    'estimated_budget', 'tenant', 'created_at')
    list_filter = ('status', 'priority', 'tenant')
    search_fields = ('number', 'title', 'department')


@admin.register(BusinessCase)
class BusinessCaseAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'recommendation', 'status',
                    'expected_roi', 'estimated_cost', 'tenant', 'created_at')
    list_filter = ('status', 'recommendation', 'tenant')
    search_fields = ('number', 'title')


@admin.register(ProjectCharter)
class ProjectCharterAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'project', 'project_manager', 'status',
                    'budget', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'title')


@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'role_title', 'influence',
                    'interest', 'engagement', 'tenant')
    list_filter = ('engagement', 'influence', 'interest', 'tenant')
    search_fields = ('name', 'organization', 'role_title', 'email')


@admin.register(KickoffTask)
class KickoffTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'owner', 'due_date', 'status',
                    'is_complete', 'tenant')
    list_filter = ('status', 'category', 'is_complete', 'tenant')
    search_fields = ('title', 'description')
