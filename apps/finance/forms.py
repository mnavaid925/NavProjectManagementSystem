"""Forms for the Financial & Billing Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    BudgetActual,
    CostCenter,
    CurrencyRate,
    FinanceInvoice,
    Payment,
)


class CostCenterForm(forms.ModelForm):
    class Meta:
        model = CostCenter
        fields = [
            'name', 'code', 'manager', 'cost_center_type',
            'budget', 'actual_cost', 'status', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'manager' in self.fields:
                self.fields['manager'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('manager',):
            if opt in self.fields:
                self.fields[opt].required = False


class FinanceInvoiceForm(forms.ModelForm):
    class Meta:
        model = FinanceInvoice
        fields = [
            'client_name', 'project', 'cost_center', 'amount', 'tax_amount',
            'currency', 'status', 'issue_date', 'due_date', 'paid_date', 'notes',
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'cost_center' in self.fields:
                self.fields['cost_center'].queryset = CostCenter.objects.filter(tenant=tenant)
        for opt in ('project', 'cost_center'):
            if opt in self.fields:
                self.fields[opt].required = False


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'invoice', 'amount', 'currency', 'method',
            'status', 'payment_date', 'reference',
        ]
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'invoice' in self.fields:
                self.fields['invoice'].queryset = FinanceInvoice.objects.filter(tenant=tenant)
        for opt in ('invoice',):
            if opt in self.fields:
                self.fields[opt].required = False


class BudgetActualForm(forms.ModelForm):
    class Meta:
        model = BudgetActual
        fields = [
            'project', 'cost_center', 'period', 'category',
            'budget_amount', 'actual_amount', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'cost_center' in self.fields:
                self.fields['cost_center'].queryset = CostCenter.objects.filter(tenant=tenant)
        for opt in ('project', 'cost_center'):
            if opt in self.fields:
                self.fields[opt].required = False


class CurrencyRateForm(forms.ModelForm):
    class Meta:
        model = CurrencyRate
        fields = [
            'base_currency', 'target_currency', 'rate',
            'effective_date', 'source', 'status',
        ]
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
