from django.contrib import admin

from .models import (
    BoardCard,
    BoardColumn,
    PriorityScore,
    WorkDependency,
    WorkItem,
)


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'item_type', 'priority', 'status',
                    'assignee', 'project', 'tenant', 'created_at')
    list_filter = ('status', 'item_type', 'priority', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(PriorityScore)
class PriorityScoreAdmin(admin.ModelAdmin):
    list_display = ('work_item', 'method', 'urgency', 'business_value',
                    'effort', 'score', 'scored_by', 'tenant', 'created_at')
    list_filter = ('method', 'urgency', 'tenant')
    search_fields = ('work_item__number', 'work_item__title', 'rationale')


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'column_type', 'order', 'wip_limit',
                    'is_done_column', 'tenant', 'created_at')
    list_filter = ('column_type', 'is_done_column', 'tenant')
    search_fields = ('name', 'description')


@admin.register(BoardCard)
class BoardCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'work_item', 'column', 'position', 'progress',
                    'is_blocked', 'tenant', 'created_at')
    list_filter = ('is_blocked', 'column', 'tenant')
    search_fields = ('title',)


@admin.register(WorkDependency)
class WorkDependencyAdmin(admin.ModelAdmin):
    list_display = ('work_item', 'depends_on', 'dependency_type', 'status',
                    'lag_days', 'tenant', 'created_at')
    list_filter = ('dependency_type', 'status', 'tenant')
    search_fields = ('work_item__title', 'depends_on__title', 'notes')
