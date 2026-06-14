"""Forms for the Portfolio & Program Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User

from .models import (
    CapacityPlan,
    Portfolio,
    Program,
    ProgramDependency,
    StrategicGoal,
)


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = [
            'name', 'description', 'portfolio_manager', 'status',
            'health', 'strategic_priority', 'total_budget',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'portfolio_manager' in self.fields:
                self.fields['portfolio_manager'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('portfolio_manager',):
            if opt in self.fields:
                self.fields[opt].required = False


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = [
            'portfolio', 'name', 'description', 'program_manager',
            'status', 'health', 'start_date', 'end_date', 'budget',
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
            if 'portfolio' in self.fields:
                self.fields['portfolio'].queryset = Portfolio.objects.filter(tenant=tenant)
            if 'program_manager' in self.fields:
                self.fields['program_manager'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('portfolio', 'program_manager'):
            if opt in self.fields:
                self.fields[opt].required = False


class ProgramDependencyForm(forms.ModelForm):
    class Meta:
        model = ProgramDependency
        fields = [
            'program', 'depends_on', 'dependency_type',
            'status', 'lag_days', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'program' in self.fields:
                self.fields['program'].queryset = Program.objects.filter(tenant=tenant)
            if 'depends_on' in self.fields:
                self.fields['depends_on'].queryset = Program.objects.filter(tenant=tenant)
        for opt in ('depends_on',):
            if opt in self.fields:
                self.fields[opt].required = False


class StrategicGoalForm(forms.ModelForm):
    class Meta:
        model = StrategicGoal
        fields = [
            'title', 'description', 'portfolio', 'category',
            'alignment_score', 'priority', 'target_date', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'portfolio' in self.fields:
                self.fields['portfolio'].queryset = Portfolio.objects.filter(tenant=tenant)
        for opt in ('portfolio',):
            if opt in self.fields:
                self.fields[opt].required = False


class CapacityPlanForm(forms.ModelForm):
    class Meta:
        model = CapacityPlan
        fields = [
            'portfolio', 'period', 'team', 'demand_hours',
            'capacity_hours', 'status', 'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'portfolio' in self.fields:
                self.fields['portfolio'].queryset = Portfolio.objects.filter(tenant=tenant)
        for opt in ('portfolio',):
            if opt in self.fields:
                self.fields[opt].required = False
