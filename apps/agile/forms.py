"""Forms for the Agile & Scrum Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    BacklogItem,
    Epic,
    Release,
    Retrospective,
    Sprint,
)


class EpicForm(forms.ModelForm):
    class Meta:
        model = Epic
        fields = [
            'title', 'description', 'project', 'owner',
            'status', 'priority', 'business_value',
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


class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = [
            'name', 'project', 'goal', 'status', 'start_date', 'end_date',
            'capacity_points', 'committed_points', 'completed_points',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
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


class BacklogItemForm(forms.ModelForm):
    class Meta:
        model = BacklogItem
        fields = [
            'title', 'description', 'item_type', 'epic', 'sprint',
            'status', 'priority', 'story_points', 'assignee',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'epic' in self.fields:
                self.fields['epic'].queryset = Epic.objects.filter(tenant=tenant)
            if 'sprint' in self.fields:
                self.fields['sprint'].queryset = Sprint.objects.filter(tenant=tenant)
            if 'assignee' in self.fields:
                self.fields['assignee'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('epic', 'sprint', 'assignee'):
            if opt in self.fields:
                self.fields[opt].required = False


class ReleaseForm(forms.ModelForm):
    class Meta:
        model = Release
        fields = [
            'name', 'version', 'project', 'description',
            'status', 'release_date', 'release_manager',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'release_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'release_manager' in self.fields:
                self.fields['release_manager'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'release_manager'):
            if opt in self.fields:
                self.fields[opt].required = False


class RetrospectiveForm(forms.ModelForm):
    class Meta:
        model = Retrospective
        fields = [
            'sprint', 'title', 'retro_date', 'facilitator', 'went_well',
            'needs_improvement', 'action_items', 'team_health_score', 'status',
        ]
        widgets = {
            'retro_date': forms.DateInput(attrs={'type': 'date'}),
            'went_well': forms.Textarea(attrs={'rows': 3}),
            'needs_improvement': forms.Textarea(attrs={'rows': 3}),
            'action_items': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'sprint' in self.fields:
                self.fields['sprint'].queryset = Sprint.objects.filter(tenant=tenant)
            if 'facilitator' in self.fields:
                self.fields['facilitator'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('sprint', 'facilitator'):
            if opt in self.fields:
                self.fields[opt].required = False
