"""Forms for the Integration & API Hub module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets. The ApiKey
form deliberately excludes ``hashed_key`` (never expose the raw/hashed key).
"""
from django import forms

from apps.accounts.models import User

from .models import (
    ApiKey,
    Connector,
    SyncJob,
    SyncLog,
    Webhook,
)


class ConnectorForm(forms.ModelForm):
    class Meta:
        model = Connector
        # last_sync_at is a system-set timestamp (shown read-only on the detail
        # page), not a user-editable field.
        fields = [
            'name', 'category', 'provider', 'auth_type',
            'base_url', 'owner', 'status',
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


class SyncJobForm(forms.ModelForm):
    class Meta:
        model = SyncJob
        # last_run_at / next_run_at are system/schedule-managed timestamps, not
        # user-editable (shown read-only on the detail page).
        fields = [
            'name', 'connector', 'direction', 'schedule',
            'records_synced', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'connector' in self.fields:
                self.fields['connector'].queryset = Connector.objects.filter(tenant=tenant)
        for opt in ('connector',):
            if opt in self.fields:
                self.fields[opt].required = False


class SyncLogForm(forms.ModelForm):
    class Meta:
        model = SyncLog
        # logged_at is a system-set timestamp (shown read-only on the detail page).
        fields = [
            'connector', 'sync_job', 'level', 'message',
            'records_processed', 'status',
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'connector' in self.fields:
                self.fields['connector'].queryset = Connector.objects.filter(tenant=tenant)
            if 'sync_job' in self.fields:
                self.fields['sync_job'].queryset = SyncJob.objects.filter(tenant=tenant)
        for opt in ('connector', 'sync_job'):
            if opt in self.fields:
                self.fields[opt].required = False


class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        # WARNING: 'secret' is intentionally excluded - never round-trip the
        # plaintext signing secret through a form (mirrors AutomationHookForm /
        # ApiKeyForm). Rotate it via a dedicated write-only flow if needed.
        # 'last_triggered_at' is a system-set timestamp (read-only on detail).
        fields = [
            'name', 'target_url', 'event', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class ApiKeyForm(forms.ModelForm):
    class Meta:
        model = ApiKey
        # WARNING: hashed_key is intentionally excluded - never expose the raw or hashed key via a form.
        fields = [
            'name', 'key_prefix', 'scopes', 'owner',
            'expires_at', 'status',
        ]
        widgets = {
            'expires_at': forms.DateInput(attrs={'type': 'date'}),
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
