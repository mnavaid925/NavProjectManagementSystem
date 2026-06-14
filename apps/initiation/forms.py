"""Forms for the Project Initiation & Charter module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    BusinessCase,
    KickoffTask,
    ProjectCharter,
    ProjectRequest,
    Stakeholder,
)


class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ProjectRequest
        fields = [
            'title', 'department', 'requested_by', 'description',
            'expected_benefit', 'estimated_budget', 'priority', 'status',
            'target_start_date', 'project',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expected_benefit': forms.Textarea(attrs={'rows': 3}),
            'target_start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'requested_by' in self.fields:
                self.fields['requested_by'].queryset = User.objects.filter(tenant=tenant)
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        for opt in ('requested_by', 'project'):
            if opt in self.fields:
                self.fields[opt].required = False


class BusinessCaseForm(forms.ModelForm):
    class Meta:
        model = BusinessCase
        fields = [
            'title', 'request', 'summary', 'problem_statement', 'expected_roi',
            'estimated_cost', 'estimated_benefit', 'payback_months',
            'recommendation', 'status',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'problem_statement': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'request' in self.fields:
                self.fields['request'].queryset = ProjectRequest.objects.filter(tenant=tenant)
        for opt in ('request',):
            if opt in self.fields:
                self.fields[opt].required = False


class ProjectCharterForm(forms.ModelForm):
    class Meta:
        model = ProjectCharter
        fields = [
            'title', 'project', 'sponsor', 'project_manager', 'objectives',
            'scope_summary', 'success_criteria', 'start_date', 'end_date',
            'budget', 'status',
        ]
        widgets = {
            'objectives': forms.Textarea(attrs={'rows': 3}),
            'scope_summary': forms.Textarea(attrs={'rows': 3}),
            'success_criteria': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            for uf in ('sponsor', 'project_manager'):
                if uf in self.fields:
                    self.fields[uf].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'sponsor', 'project_manager'):
            if opt in self.fields:
                self.fields[opt].required = False


class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = [
            'name', 'organization', 'role_title', 'email', 'project',
            'influence', 'interest', 'engagement', 'communication_preference',
            'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        for opt in ('project',):
            if opt in self.fields:
                self.fields[opt].required = False


class KickoffTaskForm(forms.ModelForm):
    class Meta:
        model = KickoffTask
        fields = [
            'title', 'project', 'charter', 'description', 'owner',
            'category', 'due_date', 'status', 'is_complete',
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
            if 'charter' in self.fields:
                self.fields['charter'].queryset = ProjectCharter.objects.filter(tenant=tenant)
            if 'owner' in self.fields:
                self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'charter', 'owner'):
            if opt in self.fields:
                self.fields[opt].required = False
