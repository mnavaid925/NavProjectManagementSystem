"""Forms for the System Administration & Security module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User

from .models import (
    AccessReview,
    BackupJob,
    ComplianceItem,
    SecurityPolicy,
    SystemHealthMetric,
)


class SecurityPolicyForm(forms.ModelForm):
    class Meta:
        model = SecurityPolicy
        fields = [
            'name', 'policy_type', 'description', 'enforcement_level',
            'last_reviewed', 'status',
        ]
        widgets = {
            'last_reviewed': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class ComplianceItemForm(forms.ModelForm):
    class Meta:
        model = ComplianceItem
        fields = [
            'framework', 'control_id', 'title', 'owner', 'due_date', 'status',
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'owner' in self.fields:
                self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('owner',):
            if opt in self.fields:
                self.fields[opt].required = False


class BackupJobForm(forms.ModelForm):
    class Meta:
        model = BackupJob
        # last_run_at is a system-set timestamp (read-only on the detail page).
        fields = [
            'name', 'backup_type', 'schedule', 'destination', 'size_mb',
            'retention_days', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class SystemHealthMetricForm(forms.ModelForm):
    class Meta:
        model = SystemHealthMetric
        # recorded_at is a system-set timestamp (read-only on the detail page).
        fields = [
            'metric_name', 'category', 'value', 'unit', 'threshold',
            'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class AccessReviewForm(forms.ModelForm):
    class Meta:
        model = AccessReview
        fields = [
            'title', 'reviewer', 'scope', 'users_reviewed', 'findings',
            'due_date', 'completed_date', 'status',
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'type': 'date'}),
            'findings': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'reviewer' in self.fields:
                self.fields['reviewer'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('reviewer',):
            if opt in self.fields:
                self.fields[opt].required = False
