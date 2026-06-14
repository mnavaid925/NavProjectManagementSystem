"""Forms for the Risk & Issue Management module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import Issue, Risk, RiskAnalysis, RiskResponse, RiskReview


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = [
            'title', 'project', 'description', 'category', 'probability',
            'impact', 'status', 'owner', 'identified_date',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'identified_date': forms.DateInput(attrs={'type': 'date'}),
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


class RiskAnalysisForm(forms.ModelForm):
    class Meta:
        model = RiskAnalysis
        fields = [
            'risk', 'analysis_type', 'probability_pct', 'impact_cost',
            'risk_level', 'notes', 'analyzed_by',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'risk' in self.fields:
                self.fields['risk'].queryset = Risk.objects.filter(tenant=tenant)
            if 'analyzed_by' in self.fields:
                self.fields['analyzed_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('analyzed_by',):
            if opt in self.fields:
                self.fields[opt].required = False


class RiskResponseForm(forms.ModelForm):
    class Meta:
        model = RiskResponse
        fields = [
            'risk', 'strategy', 'description', 'action_owner',
            'planned_action', 'cost', 'trigger_condition', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'risk' in self.fields:
                self.fields['risk'].queryset = Risk.objects.filter(tenant=tenant)
            if 'action_owner' in self.fields:
                self.fields['action_owner'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('action_owner',):
            if opt in self.fields:
                self.fields[opt].required = False


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            'title', 'project', 'description', 'severity', 'priority',
            'status', 'assigned_to', 'raised_date', 'resolved_date',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'raised_date': forms.DateInput(attrs={'type': 'date'}),
            'resolved_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'assigned_to' in self.fields:
                self.fields['assigned_to'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'assigned_to'):
            if opt in self.fields:
                self.fields[opt].required = False


class RiskReviewForm(forms.ModelForm):
    class Meta:
        model = RiskReview
        fields = [
            'title', 'project', 'review_date', 'reviewed_by', 'summary',
            'risks_reviewed', 'top_risk', 'status',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'review_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'reviewed_by' in self.fields:
                self.fields['reviewed_by'].queryset = User.objects.filter(tenant=tenant)
            if 'top_risk' in self.fields:
                self.fields['top_risk'].queryset = Risk.objects.filter(tenant=tenant)
        for opt in ('project', 'reviewed_by', 'top_risk'):
            if opt in self.fields:
                self.fields[opt].required = False
