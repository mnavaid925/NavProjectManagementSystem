from django.contrib import admin

from .models import (
    Allocation,
    DemandForecast,
    Resource,
    Skill,
    TeamAssignment,
    TimeEntry,
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'category')
    list_filter = ('category', 'tenant')
    search_fields = ('name', 'description')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'resource_type', 'job_title', 'department',
                    'capacity_hours_per_week', 'is_active')
    list_filter = ('resource_type', 'is_active', 'tenant')
    search_fields = ('name', 'email', 'job_title', 'department')
    filter_horizontal = ('skills',)


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ('resource', 'tenant', 'project', 'allocation_percent',
                    'allocated_hours', 'status', 'start_date')
    list_filter = ('status', 'tenant')
    search_fields = ('resource__name', 'notes')


@admin.register(TeamAssignment)
class TeamAssignmentAdmin(admin.ModelAdmin):
    list_display = ('resource', 'tenant', 'project', 'role_on_project',
                    'is_lead', 'status')
    list_filter = ('status', 'is_lead', 'tenant')
    search_fields = ('resource__name', 'role_on_project')


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ('title', 'tenant', 'period', 'skill', 'demand_hours',
                    'capacity_hours', 'status')
    list_filter = ('status', 'tenant')
    search_fields = ('title', 'period')


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('number', 'tenant', 'resource', 'project', 'work_date',
                    'hours', 'is_billable', 'status')
    list_filter = ('status', 'is_billable', 'tenant')
    search_fields = ('number', 'description', 'resource__name')
