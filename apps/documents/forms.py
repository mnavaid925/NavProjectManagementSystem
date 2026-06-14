"""Forms for the Document & Knowledge Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets. The custom
list filters (active/inactive, checked_out yes/no) are handled in the views,
not here.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    Document,
    DocumentTemplate,
    DocumentVersion,
    KnowledgeArticle,
    RetentionPolicy,
)


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'title', 'project', 'category', 'folder', 'status', 'owner',
            'doc_url', 'current_version', 'is_confidential', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'owner' in self.fields:
                self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'owner'):
            if opt in self.fields:
                self.fields[opt].required = False


class DocumentTemplateForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = [
            'name', 'category', 'doc_format', 'body', 'version',
            'is_active', 'created_by', 'description',
        ]
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'created_by' in self.fields:
                self.fields['created_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('created_by',):
            if opt in self.fields:
                self.fields[opt].required = False


class DocumentVersionForm(forms.ModelForm):
    class Meta:
        model = DocumentVersion
        fields = [
            'document', 'version_no', 'change_summary', 'author',
            'checked_out_by', 'is_checked_out', 'status', 'file_url',
        ]
        widgets = {
            'change_summary': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'document' in self.fields:
                self.fields['document'].queryset = Document.objects.filter(tenant=tenant)
            if 'author' in self.fields:
                self.fields['author'].queryset = User.objects.filter(tenant=tenant)
            if 'checked_out_by' in self.fields:
                self.fields['checked_out_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('author', 'checked_out_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class KnowledgeArticleForm(forms.ModelForm):
    class Meta:
        model = KnowledgeArticle
        # views_count is a programmatic read counter — excluded so users can't set it via POST.
        fields = [
            'title', 'project', 'category', 'body', 'tags',
            'author', 'status',
        ]
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'author' in self.fields:
                self.fields['author'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'author'):
            if opt in self.fields:
                self.fields[opt].required = False


class RetentionPolicyForm(forms.ModelForm):
    class Meta:
        model = RetentionPolicy
        fields = [
            'name', 'applies_to', 'retention_period_months', 'action_after',
            'legal_hold', 'is_active', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
