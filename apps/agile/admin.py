from django.contrib import admin

from .models import (
    BacklogItem,
    Epic,
    Release,
    Retrospective,
    Sprint,
)


@admin.register(Epic)
class EpicAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'project', 'status', 'priority',
                    'business_value', 'owner', 'tenant', 'created_at')
    list_filter = ('status', 'priority', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'project', 'status', 'start_date',
                    'end_date', 'capacity_points', 'committed_points',
                    'completed_points', 'tenant')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'name', 'goal')


@admin.register(BacklogItem)
class BacklogItemAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'item_type', 'epic', 'sprint', 'status',
                    'priority', 'story_points', 'assignee', 'tenant', 'created_at')
    list_filter = ('item_type', 'status', 'priority', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'version', 'project', 'status',
                    'release_date', 'release_manager', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'name', 'version')


@admin.register(Retrospective)
class RetrospectiveAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'sprint', 'retro_date', 'facilitator',
                    'team_health_score', 'status', 'tenant')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'title', 'went_well', 'needs_improvement')
