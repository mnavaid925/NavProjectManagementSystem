"""Forms for the Time & Attendance Tracking module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    LeaveRecord,
    Timesheet,
    TimesheetApproval,
    TimesheetLine,
    UtilizationSnapshot,
)


class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = [
            'owner', 'project', 'period_start', 'period_end', 'status',
            'total_hours', 'billable_hours', 'overtime_hours', 'notes',
        ]
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'owner' in self.fields:
                self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        for opt in ('owner', 'project'):
            if opt in self.fields:
                self.fields[opt].required = False


class TimesheetLineForm(forms.ModelForm):
    class Meta:
        model = TimesheetLine
        fields = [
            'timesheet', 'project', 'work_date', 'hours',
            'activity', 'is_billable', 'description',
        ]
        widgets = {
            'work_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'timesheet' in self.fields:
                self.fields['timesheet'].queryset = Timesheet.objects.filter(tenant=tenant)
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        for opt in ('project',):
            if opt in self.fields:
                self.fields[opt].required = False


class TimesheetApprovalForm(forms.ModelForm):
    class Meta:
        model = TimesheetApproval
        fields = [
            'timesheet', 'approver', 'decision', 'level', 'comments', 'decided_at',
        ]
        widgets = {
            'decided_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        self.fields['decided_at'].input_formats = ['%Y-%m-%dT%H:%M']
        if tenant is not None:
            if 'timesheet' in self.fields:
                self.fields['timesheet'].queryset = Timesheet.objects.filter(tenant=tenant)
            if 'approver' in self.fields:
                self.fields['approver'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('approver',):
            if opt in self.fields:
                self.fields[opt].required = False


class LeaveRecordForm(forms.ModelForm):
    class Meta:
        model = LeaveRecord
        fields = [
            'owner', 'leave_type', 'start_date', 'end_date', 'days',
            'status', 'reason', 'approved_by',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'owner' in self.fields:
                self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
            if 'approved_by' in self.fields:
                self.fields['approved_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('owner', 'approved_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class UtilizationSnapshotForm(forms.ModelForm):
    class Meta:
        model = UtilizationSnapshot
        fields = [
            'owner', 'project', 'period', 'capacity_hours',
            'billable_hours', 'non_billable_hours', 'utilization_pct',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'owner' in self.fields:
                self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        for opt in ('owner', 'project'):
            if opt in self.fields:
                self.fields[opt].required = False
