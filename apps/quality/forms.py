"""Forms for the Quality Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    DeliverableSignoff,
    ImprovementAction,
    Inspection,
    QualityAudit,
    QualityStandard,
)


class QualityStandardForm(forms.ModelForm):
    class Meta:
        model = QualityStandard
        fields = [
            'code', 'name', 'project', 'description', 'category',
            'acceptance_criteria', 'version', 'status', 'owner',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'acceptance_criteria': forms.Textarea(attrs={'rows': 3}),
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


class QualityAuditForm(forms.ModelForm):
    class Meta:
        model = QualityAudit
        fields = [
            'title', 'project', 'standard', 'audit_date', 'auditor',
            'audit_type', 'findings_count', 'result', 'status', 'notes',
        ]
        widgets = {
            'audit_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'standard' in self.fields:
                self.fields['standard'].queryset = QualityStandard.objects.filter(tenant=tenant)
            if 'auditor' in self.fields:
                self.fields['auditor'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'standard', 'auditor'):
            if opt in self.fields:
                self.fields[opt].required = False


class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = [
            'title', 'project', 'inspection_date', 'inspector', 'deliverable',
            'defects_found', 'result', 'status', 'notes',
        ]
        widgets = {
            'inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'inspector' in self.fields:
                self.fields['inspector'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'inspector'):
            if opt in self.fields:
                self.fields[opt].required = False


class ImprovementActionForm(forms.ModelForm):
    class Meta:
        model = ImprovementAction
        fields = [
            'title', 'project', 'description', 'source', 'priority',
            'owner', 'due_date', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
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


class DeliverableSignoffForm(forms.ModelForm):
    class Meta:
        model = DeliverableSignoff
        fields = [
            'deliverable_name', 'project', 'description', 'submitted_by',
            'approver', 'submitted_date', 'signoff_date', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'submitted_date': forms.DateInput(attrs={'type': 'date'}),
            'signoff_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            for uf in ('submitted_by', 'approver'):
                if uf in self.fields:
                    self.fields[uf].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'submitted_by', 'approver'):
            if opt in self.fields:
                self.fields[opt].required = False
