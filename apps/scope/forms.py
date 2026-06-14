"""Forms for the Scope & Requirements Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    ChangeRequest,
    Requirement,
    RequirementTrace,
    ScopeStatement,
    ScopeVerification,
)


class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = [
            'title', 'project', 'description', 'requirement_type',
            'moscow', 'source', 'status', 'owner',
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


class RequirementTraceForm(forms.ModelForm):
    class Meta:
        model = RequirementTrace
        fields = [
            'requirement', 'trace_type', 'linked_artifact',
            'artifact_type', 'verified', 'notes',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'requirement' in self.fields:
                self.fields['requirement'].queryset = Requirement.objects.filter(tenant=tenant)


class ScopeStatementForm(forms.ModelForm):
    class Meta:
        model = ScopeStatement
        fields = [
            'title', 'project', 'in_scope', 'out_of_scope', 'assumptions',
            'constraints', 'deliverables', 'status', 'approved_by',
        ]
        widgets = {
            'in_scope': forms.Textarea(attrs={'rows': 3}),
            'out_of_scope': forms.Textarea(attrs={'rows': 3}),
            'assumptions': forms.Textarea(attrs={'rows': 3}),
            'constraints': forms.Textarea(attrs={'rows': 3}),
            'deliverables': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'approved_by' in self.fields:
                self.fields['approved_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'approved_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class ChangeRequestForm(forms.ModelForm):
    class Meta:
        model = ChangeRequest
        fields = [
            'title', 'project', 'requirement', 'description', 'change_type',
            'impact_summary', 'priority', 'status', 'requested_by', 'decided_at',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'impact_summary': forms.Textarea(attrs={'rows': 3}),
            'decided_at': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'requirement' in self.fields:
                self.fields['requirement'].queryset = Requirement.objects.filter(tenant=tenant)
            if 'requested_by' in self.fields:
                self.fields['requested_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'requirement', 'requested_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class ScopeVerificationForm(forms.ModelForm):
    class Meta:
        model = ScopeVerification
        fields = [
            'title', 'project', 'scope_statement', 'verification_date',
            'verified_by', 'deliverable', 'result', 'scope_creep_flag',
            'notes', 'status',
        ]
        widgets = {
            'verification_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'scope_statement' in self.fields:
                self.fields['scope_statement'].queryset = ScopeStatement.objects.filter(tenant=tenant)
            if 'verified_by' in self.fields:
                self.fields['verified_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'scope_statement', 'verified_by'):
            if opt in self.fields:
                self.fields[opt].required = False
