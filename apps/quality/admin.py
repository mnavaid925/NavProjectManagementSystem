from django.contrib import admin

from .models import (
    DeliverableSignoff,
    ImprovementAction,
    Inspection,
    QualityAudit,
    QualityStandard,
)


@admin.register(QualityStandard)
class QualityStandardAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'version', 'status',
                    'project', 'owner', 'tenant', 'created_at')
    list_filter = ('status', 'category', 'tenant')
    search_fields = ('code', 'name', 'description')


@admin.register(QualityAudit)
class QualityAuditAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'audit_type', 'audit_date', 'findings_count',
                    'result', 'status', 'standard', 'tenant', 'created_at')
    list_filter = ('status', 'audit_type', 'result', 'tenant')
    search_fields = ('number', 'title')


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'deliverable', 'inspection_date',
                    'defects_found', 'result', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'result', 'tenant')
    search_fields = ('number', 'title', 'deliverable')


@admin.register(ImprovementAction)
class ImprovementActionAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'source', 'priority', 'due_date',
                    'status', 'owner', 'tenant', 'created_at')
    list_filter = ('status', 'source', 'priority', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(DeliverableSignoff)
class DeliverableSignoffAdmin(admin.ModelAdmin):
    list_display = ('number', 'deliverable_name', 'project', 'submitted_by',
                    'approver', 'submitted_date', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'deliverable_name')
