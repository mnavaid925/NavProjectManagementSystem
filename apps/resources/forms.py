"""Forms for the Resource Management module. All FK/M2M querysets are tenant-scoped."""
from django import forms

from .models import (
    Allocation,
    DemandForecast,
    Resource,
    Skill,
    TeamAssignment,
    TimeEntry,
)


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            'name', 'resource_type', 'email', 'job_title', 'department',
            'location', 'capacity_hours_per_week', 'cost_rate', 'user',
            'skills', 'is_active',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        from apps.accounts.models import User
        if tenant is not None:
            if 'user' in self.fields:
                self.fields['user'].queryset = User.objects.filter(tenant=tenant)
            if 'skills' in self.fields:
                self.fields['skills'].queryset = Skill.objects.filter(tenant=tenant)
        for opt in ('user', 'skills'):
            if opt in self.fields:
                self.fields[opt].required = False


class AllocationForm(forms.ModelForm):
    class Meta:
        model = Allocation
        fields = [
            'resource', 'project', 'allocation_percent', 'allocated_hours',
            'start_date', 'end_date', 'status', 'notes',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        from apps.projects.models import Project
        if tenant is not None:
            if 'resource' in self.fields:
                self.fields['resource'].queryset = Resource.objects.filter(tenant=tenant)
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        if 'resource' in self.fields:
            self.fields['resource'].required = True
        if 'project' in self.fields:
            self.fields['project'].required = False


class TeamAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeamAssignment
        fields = [
            'resource', 'project', 'role_on_project', 'is_lead',
            'start_date', 'end_date', 'status',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        from apps.projects.models import Project
        if tenant is not None:
            if 'resource' in self.fields:
                self.fields['resource'].queryset = Resource.objects.filter(tenant=tenant)
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        if 'resource' in self.fields:
            self.fields['resource'].required = True
        if 'role_on_project' in self.fields:
            self.fields['role_on_project'].required = True
        if 'project' in self.fields:
            self.fields['project'].required = False


class DemandForecastForm(forms.ModelForm):
    class Meta:
        model = DemandForecast
        fields = [
            'title', 'project', 'skill', 'period', 'demand_hours',
            'capacity_hours', 'status', 'notes',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        from apps.projects.models import Project
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'skill' in self.fields:
                self.fields['skill'].queryset = Skill.objects.filter(tenant=tenant)
        for opt in ('project', 'skill'):
            if opt in self.fields:
                self.fields[opt].required = False


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = [
            'resource', 'project', 'work_date', 'hours',
            'is_billable', 'status', 'description',
        ]
        widgets = {
            'work_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        from apps.projects.models import Project
        if tenant is not None:
            if 'resource' in self.fields:
                self.fields['resource'].queryset = Resource.objects.filter(tenant=tenant)
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        if 'resource' in self.fields:
            self.fields['resource'].required = True
        if 'project' in self.fields:
            self.fields['project'].required = False
