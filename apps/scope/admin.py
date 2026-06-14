from django.contrib import admin

from .models import (
    ChangeRequest,
    Requirement,
    RequirementTrace,
    ScopeStatement,
    ScopeVerification,
)


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'requirement_type', 'moscow', 'status',
                    'owner', 'tenant', 'created_at')
    list_filter = ('status', 'requirement_type', 'moscow', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(RequirementTrace)
class RequirementTraceAdmin(admin.ModelAdmin):
    list_display = ('requirement', 'linked_artifact', 'trace_type',
                    'artifact_type', 'verified', 'tenant', 'created_at')
    list_filter = ('trace_type', 'artifact_type', 'verified', 'tenant')
    search_fields = ('linked_artifact', 'notes', 'requirement__title')


@admin.register(ScopeStatement)
class ScopeStatementAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'project', 'status', 'approved_by',
                    'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'title')


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'change_type', 'priority', 'status',
                    'requested_by', 'tenant', 'created_at')
    list_filter = ('status', 'change_type', 'priority', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(ScopeVerification)
class ScopeVerificationAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'deliverable', 'verification_date',
                    'result', 'scope_creep_flag', 'status', 'tenant')
    list_filter = ('status', 'result', 'scope_creep_flag', 'tenant')
    search_fields = ('number', 'title', 'deliverable')
