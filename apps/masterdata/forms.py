"""Forms for the Master Data & Configuration module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets.
"""
from django import forms

from apps.accounts.models import User

from .models import (
    CustomField,
    LocalizationSetting,
    OrgUnit,
    ProjectTemplate,
    Team,
)


class ProjectTemplateForm(forms.ModelForm):
    class Meta:
        model = ProjectTemplate
        fields = [
            'name', 'methodology', 'category', 'default_duration_days',
            'phase_count', 'description', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class CustomFieldForm(forms.ModelForm):
    class Meta:
        model = CustomField
        fields = [
            'label', 'field_type', 'entity_type', 'is_required',
            'options', 'help_text', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant


class OrgUnitForm(forms.ModelForm):
    class Meta:
        model = OrgUnit
        fields = [
            'name', 'unit_type', 'parent', 'manager', 'code', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'parent' in self.fields:
                self.fields['parent'].queryset = OrgUnit.objects.filter(tenant=tenant)
            if 'manager' in self.fields:
                self.fields['manager'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('parent', 'manager'):
            if opt in self.fields:
                self.fields[opt].required = False


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'name', 'org_unit', 'team_lead', 'member_count',
            'focus_area', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'org_unit' in self.fields:
                self.fields['org_unit'].queryset = OrgUnit.objects.filter(tenant=tenant)
            if 'team_lead' in self.fields:
                self.fields['team_lead'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('org_unit', 'team_lead'):
            if opt in self.fields:
                self.fields[opt].required = False


class LocalizationSettingForm(forms.ModelForm):
    class Meta:
        model = LocalizationSetting
        fields = [
            'locale_code', 'language', 'timezone', 'date_format',
            'number_format', 'currency', 'is_default', 'status',
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
