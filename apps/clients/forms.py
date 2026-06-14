"""Forms for the Client & External Collaboration module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.projects.models import Project

from .models import (
    ClientAccess,
    ClientFeedback,
    ClientInvoice,
    ExternalVendor,
    SOWContract,
)


class ClientAccessForm(forms.ModelForm):
    class Meta:
        model = ClientAccess
        fields = [
            'client_name', 'project', 'contact_name', 'contact_email',
            'access_level', 'portal_enabled', 'status', 'notes',
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


class ClientFeedbackForm(forms.ModelForm):
    class Meta:
        model = ClientFeedback
        fields = [
            'client_name', 'project', 'subject', 'feedback_type',
            'rating', 'status', 'submitted_date', 'details',
        ]
        widgets = {
            'submitted_date': forms.DateInput(attrs={'type': 'date'}),
            'details': forms.Textarea(attrs={'rows': 3}),
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


class SOWContractForm(forms.ModelForm):
    class Meta:
        model = SOWContract
        fields = [
            'title', 'client_name', 'project', 'contract_type', 'value',
            'currency', 'start_date', 'end_date', 'status', 'signed_date',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'signed_date': forms.DateInput(attrs={'type': 'date'}),
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


class ExternalVendorForm(forms.ModelForm):
    class Meta:
        model = ExternalVendor
        fields = [
            'name', 'contact_name', 'contact_email', 'service_type',
            'status', 'rating', 'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class ClientInvoiceForm(forms.ModelForm):
    class Meta:
        model = ClientInvoice
        fields = [
            'client_name', 'project', 'contract', 'amount', 'currency',
            'billing_type', 'status', 'issue_date', 'due_date', 'paid_date',
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'contract' in self.fields:
                self.fields['contract'].queryset = SOWContract.objects.filter(tenant=tenant)
        for opt in ('project', 'contract'):
            if opt in self.fields:
                self.fields[opt].required = False
