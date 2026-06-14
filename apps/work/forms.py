"""Forms for the Task & Work Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets. Custom
list filters (blocked yes/no, etc.) are handled in the views, not here.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    BoardCard,
    BoardColumn,
    PriorityScore,
    WorkDependency,
    WorkItem,
)


class WorkItemForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = [
            'title', 'project', 'description', 'item_type', 'status',
            'priority', 'assignee', 'reporter', 'story_points',
            'estimate_hours', 'start_date', 'due_date',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            for uf in ('assignee', 'reporter'):
                if uf in self.fields:
                    self.fields[uf].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'assignee', 'reporter'):
            if opt in self.fields:
                self.fields[opt].required = False


class PriorityScoreForm(forms.ModelForm):
    class Meta:
        model = PriorityScore
        fields = [
            'work_item', 'method', 'urgency', 'business_value',
            'effort', 'score', 'rationale', 'scored_by',
        ]
        widgets = {
            'rationale': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'work_item' in self.fields:
                self.fields['work_item'].queryset = WorkItem.objects.filter(tenant=tenant)
            if 'scored_by' in self.fields:
                self.fields['scored_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('scored_by',):
            if opt in self.fields:
                self.fields[opt].required = False


class BoardColumnForm(forms.ModelForm):
    class Meta:
        model = BoardColumn
        fields = [
            'name', 'project', 'column_type', 'order',
            'wip_limit', 'is_done_column', 'description',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        for opt in ('project',):
            if opt in self.fields:
                self.fields[opt].required = False


class BoardCardForm(forms.ModelForm):
    class Meta:
        model = BoardCard
        fields = [
            'title', 'work_item', 'column', 'position', 'planned_start',
            'planned_end', 'progress', 'is_blocked', 'color',
        ]
        widgets = {
            'planned_start': forms.DateInput(attrs={'type': 'date'}),
            'planned_end': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'work_item' in self.fields:
                self.fields['work_item'].queryset = WorkItem.objects.filter(tenant=tenant)
            if 'column' in self.fields:
                self.fields['column'].queryset = BoardColumn.objects.filter(tenant=tenant)
        for opt in ('work_item', 'column'):
            if opt in self.fields:
                self.fields[opt].required = False


class WorkDependencyForm(forms.ModelForm):
    class Meta:
        model = WorkDependency
        fields = [
            'work_item', 'depends_on', 'dependency_type',
            'status', 'lag_days', 'notes',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'work_item' in self.fields:
                self.fields['work_item'].queryset = WorkItem.objects.filter(tenant=tenant)
            if 'depends_on' in self.fields:
                self.fields['depends_on'].queryset = WorkItem.objects.filter(tenant=tenant)
