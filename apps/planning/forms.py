"""Forms for Project Planning & Scheduling. All FK/M2M querysets are tenant-scoped."""
from django import forms

from .models import (
    Milestone,
    ScheduleBaseline,
    ScheduleTask,
    TaskDependency,
    WorkPackage,
)


class WorkPackageForm(forms.ModelForm):
    class Meta:
        model = WorkPackage
        fields = [
            'code', 'name', 'project', 'parent', 'description',
            'level', 'estimated_effort_hours', 'owner', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            from apps.accounts.models import User
            from apps.projects.models import Project
            self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
            parent_qs = WorkPackage.objects.filter(tenant=tenant)
            if self.instance and self.instance.pk:
                parent_qs = parent_qs.exclude(pk=self.instance.pk)
            self.fields['parent'].queryset = parent_qs
        for opt in ('project', 'parent', 'owner'):
            if opt in self.fields:
                self.fields[opt].required = False


class ScheduleTaskForm(forms.ModelForm):
    class Meta:
        model = ScheduleTask
        fields = [
            'name', 'project', 'work_package', 'description', 'assignee',
            'start_date', 'end_date', 'duration_days', 'effort_hours',
            'estimate_method', 'percent_complete', 'status', 'is_critical',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            from apps.accounts.models import User
            from apps.projects.models import Project
            self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            self.fields['assignee'].queryset = User.objects.filter(tenant=tenant)
            self.fields['work_package'].queryset = WorkPackage.objects.filter(tenant=tenant)
        for opt in ('project', 'work_package', 'assignee'):
            if opt in self.fields:
                self.fields[opt].required = False


class TaskDependencyForm(forms.ModelForm):
    class Meta:
        model = TaskDependency
        fields = ['predecessor', 'successor', 'dependency_type', 'lag_days', 'notes']

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            tasks = ScheduleTask.objects.filter(tenant=tenant)
            self.fields['predecessor'].queryset = tasks
            self.fields['successor'].queryset = tasks
        # predecessor / successor stay required; notes is optional
        if 'notes' in self.fields:
            self.fields['notes'].required = False


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = [
            'name', 'project', 'description', 'due_date', 'milestone_type',
            'gate_status', 'entry_criteria', 'exit_criteria', 'is_completed',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'entry_criteria': forms.Textarea(attrs={'rows': 3}),
            'exit_criteria': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            from apps.projects.models import Project
            self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        if 'project' in self.fields:
            self.fields['project'].required = False


class ScheduleBaselineForm(forms.ModelForm):
    class Meta:
        model = ScheduleBaseline
        fields = [
            'name', 'project', 'version', 'baseline_date', 'planned_start',
            'planned_finish', 'status', 'is_current', 'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'baseline_date': forms.DateInput(attrs={'type': 'date'}),
            'planned_start': forms.DateInput(attrs={'type': 'date'}),
            'planned_finish': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            from apps.projects.models import Project
            self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        if 'project' in self.fields:
            self.fields['project'].required = False
