from django.contrib import admin

from .models import (
    Document,
    DocumentTemplate,
    DocumentVersion,
    KnowledgeArticle,
    RetentionPolicy,
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'category', 'status', 'current_version',
                    'is_confidential', 'owner', 'tenant', 'created_at')
    list_filter = ('status', 'category', 'is_confidential', 'tenant')
    search_fields = ('number', 'title', 'folder', 'description')


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'doc_format', 'version', 'is_active',
                    'created_by', 'tenant', 'created_at')
    list_filter = ('category', 'doc_format', 'is_active', 'tenant')
    search_fields = ('name', 'description', 'body')


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_no', 'status', 'is_checked_out',
                    'author', 'checked_out_by', 'tenant', 'created_at')
    list_filter = ('status', 'is_checked_out', 'tenant')
    search_fields = ('version_no', 'change_summary', 'document__number', 'document__title')


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'category', 'status', 'views_count',
                    'author', 'tenant', 'created_at')
    list_filter = ('category', 'status', 'tenant')
    search_fields = ('number', 'title', 'body', 'tags')


@admin.register(RetentionPolicy)
class RetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'applies_to', 'retention_period_months', 'action_after',
                    'legal_hold', 'is_active', 'tenant', 'created_at')
    list_filter = ('applies_to', 'action_after', 'legal_hold', 'is_active', 'tenant')
    search_fields = ('name', 'description')
