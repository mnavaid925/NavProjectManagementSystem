"""Forms for Module 0 - Tenant & Subscription Management."""
from django import forms

from apps.core.models import Tenant

from .models import BrandingSettings, Invoice, PaymentMethod, Plan


class TenantConfigForm(forms.ModelForm):
    """Onboarding wizard: basic tenant configuration."""

    class Meta:
        model = Tenant
        fields = ['name', 'subdomain', 'contact_email', 'is_active']


class PlanForm(forms.ModelForm):
    features_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text='One feature per line.',
    )

    class Meta:
        model = Plan
        fields = [
            'name', 'slug', 'price_monthly', 'price_yearly', 'max_users',
            'max_projects', 'max_storage_gb', 'is_active', 'is_popular', 'sort_order',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and isinstance(self.instance.features, list):
            self.fields['features_text'].initial = '\n'.join(self.instance.features)

    def save(self, commit=True):
        plan = super().save(commit=False)
        raw = self.cleaned_data.get('features_text', '')
        plan.features = [line.strip() for line in raw.splitlines() if line.strip()]
        if commit:
            plan.save()
        return plan


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['subscription', 'amount', 'tax', 'status', 'issue_date', 'due_date', 'notes']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Subscription
        if tenant is not None:
            self.fields['subscription'].queryset = Subscription.objects.filter(tenant=tenant)
        self.fields['subscription'].required = False


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['type', 'brand', 'last4', 'exp_month', 'exp_year', 'holder_name', 'is_default']


class BrandingForm(forms.ModelForm):
    class Meta:
        model = BrandingSettings
        fields = [
            'logo', 'favicon', 'primary_color', 'secondary_color', 'accent_color',
            'login_background', 'email_from_name', 'email_signature',
            'custom_domain', 'enable_white_label',
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color'}),
            'email_signature': forms.Textarea(attrs={'rows': 3}),
        }
