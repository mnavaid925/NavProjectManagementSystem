from django.contrib import admin

from .models import (
    Milestone,
    ScheduleBaseline,
    ScheduleTask,
    TaskDependency,
    WorkPackage,
)


@admin.register(WorkPackage)
class WorkPackageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'tenant', 'project', 'level', 'status', 'owner')
    list_filter = ('status', 'level', 'tenant')
    search_fields = ('code', 'name', 'description')


@admin.register(ScheduleTask)
class ScheduleTaskAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'tenant', 'project', 'estimate_method',
        'percent_complete', 'status', 'is_critical',
    )
    list_filter = ('status', 'estimate_method', 'is_critical', 'tenant')
    search_fields = ('name', 'description')


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ('predecessor', 'successor', 'tenant', 'dependency_type', 'lag_days')
    list_filter = ('dependency_type', 'tenant')
    search_fields = ('notes', 'predecessor__name', 'successor__name')


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'tenant', 'project', 'milestone_type',
        'gate_status', 'due_date', 'is_completed',
    )
    list_filter = ('milestone_type', 'gate_status', 'is_completed', 'tenant')
    search_fields = ('name', 'description')


@admin.register(ScheduleBaseline)
class ScheduleBaselineAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'version', 'tenant', 'project',
        'baseline_date', 'status', 'is_current',
    )
    list_filter = ('status', 'is_current', 'tenant')
    search_fields = ('name', 'version', 'notes')
