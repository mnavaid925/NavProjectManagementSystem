"""Forms for the Reporting & Business Intelligence module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    DashboardWidget,
    DataExport,
    ExecutivePack,
    ReportDefinition,
    ReportRun,
)


class ReportDefinitionForm(forms.ModelForm):
    class Meta:
        model = ReportDefinition
        fields = [
            'name', 'category', 'data_source', 'visibility', 'project',
            'owner', 'description', 'is_scheduled', 'status',
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


class ReportRunForm(forms.ModelForm):
    class Meta:
        model = ReportRun
        # started_at is a system-set run timestamp (read-only on the detail page).
        fields = [
            'report', 'run_by', 'format', 'row_count', 'duration_ms',
            'notes', 'status',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'report' in self.fields:
                self.fields['report'].queryset = ReportDefinition.objects.filter(tenant=tenant)
            if 'run_by' in self.fields:
                self.fields['run_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('report', 'run_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class DashboardWidgetForm(forms.ModelForm):
    class Meta:
        model = DashboardWidget
        fields = [
            'title', 'widget_type', 'metric', 'data_source', 'position',
            'refresh_interval', 'owner', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'owner' in self.fields:
                self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('owner',):
            if opt in self.fields:
                self.fields[opt].required = False


class ExecutivePackForm(forms.ModelForm):
    class Meta:
        model = ExecutivePack
        fields = [
            'title', 'project', 'period', 'rag_status', 'summary',
            'prepared_by', 'published_date', 'status',
        ]
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'prepared_by' in self.fields:
                self.fields['prepared_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'prepared_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class DataExportForm(forms.ModelForm):
    class Meta:
        model = DataExport
        # completed_at is a system-set timestamp (read-only on the detail page).
        fields = [
            'name', 'export_type', 'destination', 'data_source',
            'record_count', 'requested_by', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'requested_by' in self.fields:
                self.fields['requested_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('requested_by',):
            if opt in self.fields:
                self.fields[opt].required = False
