"""Forms for the Cost & Budget Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    Budget,
    BudgetChange,
    ControlAccount,
    CostForecast,
    Expense,
)


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            'name', 'project', 'fiscal_year', 'category', 'planned_amount',
            'allocated_amount', 'currency', 'owner', 'status', 'notes',
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
            if 'owner' in self.fields:
                self.fields['owner'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'owner'):
            if opt in self.fields:
                self.fields[opt].required = False


class ControlAccountForm(forms.ModelForm):
    class Meta:
        model = ControlAccount
        fields = [
            'code', 'name', 'project', 'budget', 'manager', 'bac',
            'earned_value', 'actual_cost', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'budget' in self.fields:
                self.fields['budget'].queryset = Budget.objects.filter(tenant=tenant)
            if 'manager' in self.fields:
                self.fields['manager'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'budget', 'manager'):
            if opt in self.fields:
                self.fields[opt].required = False


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'description', 'project', 'control_account', 'category', 'amount',
            'expense_date', 'vendor', 'expense_type', 'status', 'submitted_by',
        ]
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'control_account' in self.fields:
                self.fields['control_account'].queryset = ControlAccount.objects.filter(tenant=tenant)
            if 'submitted_by' in self.fields:
                self.fields['submitted_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'control_account', 'submitted_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class CostForecastForm(forms.ModelForm):
    class Meta:
        model = CostForecast
        fields = [
            'name', 'project', 'budget', 'period', 'bac', 'eac', 'etc',
            'method', 'status', 'notes',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'budget' in self.fields:
                self.fields['budget'].queryset = Budget.objects.filter(tenant=tenant)
        for opt in ('project', 'budget'):
            if opt in self.fields:
                self.fields[opt].required = False


class BudgetChangeForm(forms.ModelForm):
    class Meta:
        model = BudgetChange
        fields = [
            'title', 'budget', 'change_type', 'amount', 'reason', 'status',
            'requested_by', 'decided_at',
        ]
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
            'decided_at': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'budget' in self.fields:
                self.fields['budget'].queryset = Budget.objects.filter(tenant=tenant)
            if 'requested_by' in self.fields:
                self.fields['requested_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('budget', 'requested_by'):
            if opt in self.fields:
                self.fields[opt].required = False
