"""Forms for the Workflow & Automation module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    ApprovalRule,
    AutomationHook,
    NotificationRule,
    RecurringRule,
    WorkflowDefinition,
)


class WorkflowDefinitionForm(forms.ModelForm):
    class Meta:
        model = WorkflowDefinition
        fields = [
            'name', 'trigger_event', 'entity_type', 'project', 'owner',
            'description', 'step_count', 'status',
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


class ApprovalRuleForm(forms.ModelForm):
    class Meta:
        model = ApprovalRule
        fields = [
            'name', 'entity_type', 'threshold_amount', 'approver',
            'escalation_hours', 'auto_approve_below', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'approver' in self.fields:
                self.fields['approver'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('approver',):
            if opt in self.fields:
                self.fields[opt].required = False


class NotificationRuleForm(forms.ModelForm):
    class Meta:
        model = NotificationRule
        fields = [
            'name', 'trigger_event', 'channel', 'lead_time_hours',
            'recipient_role', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class RecurringRuleForm(forms.ModelForm):
    class Meta:
        model = RecurringRule
        fields = [
            'name', 'frequency', 'project', 'assignee',
            'next_run_date', 'task_template', 'status',
        ]
        widgets = {
            'next_run_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'assignee' in self.fields:
                self.fields['assignee'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'assignee'):
            if opt in self.fields:
                self.fields[opt].required = False


class AutomationHookForm(forms.ModelForm):
    class Meta:
        model = AutomationHook
        # NOTE: 'secret' is intentionally excluded - the raw secret is never
        # rendered back into a form. Manage rotation via a dedicated, write-only
        # flow that encrypts at rest; never round-trip the plaintext value.
        fields = [
            'name', 'hook_type', 'target_url', 'event', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
