from django.contrib import admin

from .models import (
    DashboardWidget,
    DataExport,
    ExecutivePack,
    ReportDefinition,
    ReportRun,
)


@admin.register(ReportDefinition)
class ReportDefinitionAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'category', 'data_source', 'visibility',
                    'project', 'owner', 'is_scheduled', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'category', 'tenant')
    search_fields = ('number', 'name', 'description')


@admin.register(ReportRun)
class ReportRunAdmin(admin.ModelAdmin):
    list_display = ('number', 'report', 'run_by', 'format', 'row_count',
                    'duration_ms', 'started_at', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'format', 'tenant')
    search_fields = ('number', 'notes')


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'widget_type', 'metric', 'data_source',
                    'position', 'refresh_interval', 'owner', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'widget_type', 'tenant')
    search_fields = ('number', 'title', 'metric')


@admin.register(ExecutivePack)
class ExecutivePackAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'project', 'period', 'rag_status',
                    'prepared_by', 'published_date', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'rag_status', 'tenant')
    search_fields = ('number', 'title', 'summary')


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'export_type', 'destination', 'data_source',
                    'record_count', 'requested_by', 'completed_at', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'export_type', 'tenant')
    search_fields = ('number', 'name', 'destination')
