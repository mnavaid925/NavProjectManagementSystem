"""Tests for tenants app forms."""
import datetime

import pytest

from apps.tenants.forms import (
    BrandingForm,
    InvoiceForm,
    PaymentMethodForm,
    PlanForm,
    TenantConfigForm,
)
from apps.tenants.models import Invoice


# ---------------------------------------------------------------------------
# TenantConfigForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTenantConfigForm:
    def test_valid_minimal(self, acme_tenant):
        form = TenantConfigForm(
            data={'name': 'Acme Corp', 'subdomain': 'acme', 'contact_email': '', 'is_active': True},
            instance=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_name_required(self, acme_tenant):
        form = TenantConfigForm(
            data={'name': '', 'subdomain': 'acme', 'contact_email': '', 'is_active': True},
            instance=acme_tenant,
        )
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_invalid_email(self, acme_tenant):
        form = TenantConfigForm(
            data={'name': 'Acme', 'subdomain': 'acme', 'contact_email': 'not-an-email', 'is_active': True},
            instance=acme_tenant,
        )
        assert not form.is_valid()
        assert 'contact_email' in form.errors

    def test_no_tenant_field(self):
        """tenant is not a form field (it's a FK not included in Meta.fields)."""
        assert 'tenant' not in TenantConfigForm().fields


# ---------------------------------------------------------------------------
# PlanForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPlanForm:
    def test_valid(self):
        form = PlanForm(data={
            'name': 'Starter',
            'slug': 'starter',
            'price_monthly': '9.99',
            'price_yearly': '99.99',
            'max_users': '5',
            'max_projects': '10',
            'max_storage_gb': '5',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
            'features_text': 'Feature A\nFeature B',
        })
        assert form.is_valid(), form.errors

    def test_name_required(self):
        form = PlanForm(data={
            'name': '',
            'slug': 'starter',
            'price_monthly': '9.99',
            'price_yearly': '99.99',
            'max_users': '5',
            'max_projects': '10',
            'max_storage_gb': '5',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
        })
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_features_text_saved_as_list(self):
        form = PlanForm(data={
            'name': 'Pro',
            'slug': 'pro',
            'price_monthly': '29.99',
            'price_yearly': '299.99',
            'max_users': '25',
            'max_projects': '100',
            'max_storage_gb': '50',
            'is_active': True,
            'is_popular': True,
            'sort_order': '1',
            'features_text': 'SSO\nAPI access\nCustom domain',
        })
        assert form.is_valid(), form.errors
        plan = form.save()
        assert plan.features == ['SSO', 'API access', 'Custom domain']

    def test_features_text_optional(self):
        form = PlanForm(data={
            'name': 'Free',
            'slug': 'free',
            'price_monthly': '0',
            'price_yearly': '0',
            'max_users': '1',
            'max_projects': '1',
            'max_storage_gb': '1',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
            'features_text': '',
        })
        assert form.is_valid(), form.errors
        plan = form.save()
        assert plan.features == []

    def test_no_number_field(self):
        """'number' is not a field in PlanForm."""
        assert 'number' not in PlanForm().fields

    def test_no_tenant_field(self):
        """Plans are global; 'tenant' must not appear in PlanForm."""
        assert 'tenant' not in PlanForm().fields

    def test_invalid_price(self):
        form = PlanForm(data={
            'name': 'Bad',
            'slug': 'bad',
            'price_monthly': 'not-a-number',
            'price_yearly': '0',
            'max_users': '5',
            'max_projects': '10',
            'max_storage_gb': '5',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
        })
        assert not form.is_valid()
        assert 'price_monthly' in form.errors


# ---------------------------------------------------------------------------
# InvoiceForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestInvoiceForm:
    def test_valid_minimal(self, acme_tenant):
        form = InvoiceForm(
            data={
                'subscription': '',
                'amount': '100.00',
                'tax': '10.00',
                'status': Invoice.STATUS_DRAFT,
                'issue_date': '2025-01-01',
                'due_date': '2025-01-31',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_amount_required(self, acme_tenant):
        form = InvoiceForm(
            data={
                'subscription': '',
                'amount': '',
                'tax': '0',
                'status': Invoice.STATUS_DRAFT,
                'issue_date': '2025-01-01',
                'due_date': '2025-01-31',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'amount' in form.errors

    def test_no_number_field(self, acme_tenant):
        """auto-number is not a form field."""
        form = InvoiceForm(tenant=acme_tenant)
        assert 'number' not in form.fields

    def test_no_tenant_field(self, acme_tenant):
        """tenant is set by view, not a form field."""
        form = InvoiceForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_subscription_queryset_scoped_to_tenant(self, acme_tenant, acme_subscription):
        """Subscription dropdown only shows subs belonging to the given tenant."""
        form = InvoiceForm(tenant=acme_tenant)
        qs = form.fields['subscription'].queryset
        assert acme_subscription in qs

    def test_subscription_from_other_tenant_not_in_queryset(
        self, db, acme_tenant, globex_tenant, basic_plan, acme_subscription
    ):
        import datetime
        from apps.tenants.models import Subscription
        today = datetime.date.today()
        globex_sub = Subscription.objects.create(
            tenant=globex_tenant,
            plan=basic_plan,
            status='active',
            started_at=today,
            current_period_start=today,
            current_period_end=today + datetime.timedelta(days=30),
        )
        form = InvoiceForm(tenant=acme_tenant)
        qs = form.fields['subscription'].queryset
        assert globex_sub not in qs

    def test_invalid_status(self, acme_tenant):
        form = InvoiceForm(
            data={
                'subscription': '',
                'amount': '100.00',
                'tax': '0',
                'status': 'nonexistent_status',
                'issue_date': '2025-01-01',
                'due_date': '2025-01-31',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors


# ---------------------------------------------------------------------------
# PaymentMethodForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPaymentMethodForm:
    def test_valid(self):
        form = PaymentMethodForm(data={
            'type': 'card',
            'brand': 'Visa',
            'last4': '4242',
            'exp_month': '12',
            'exp_year': '2027',
            'holder_name': 'Test User',
            'is_default': True,
        })
        assert form.is_valid(), form.errors

    def test_no_tenant_field(self):
        assert 'tenant' not in PaymentMethodForm().fields

    def test_invalid_type(self):
        form = PaymentMethodForm(data={
            'type': 'crypto',
            'brand': '',
            'last4': '',
            'exp_month': '',
            'exp_year': '',
            'holder_name': '',
            'is_default': False,
        })
        assert not form.is_valid()
        assert 'type' in form.errors

    def test_optional_fields(self):
        """brand, last4, exp_month/year, holder_name are optional."""
        form = PaymentMethodForm(data={
            'type': 'paypal',
            'brand': '',
            'last4': '',
            'exp_month': '',
            'exp_year': '',
            'holder_name': '',
            'is_default': False,
        })
        assert form.is_valid(), form.errors


# ---------------------------------------------------------------------------
# BrandingForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestBrandingForm:
    def test_valid_minimal(self):
        form = BrandingForm(data={
            'primary_color': '#2563eb',
            'secondary_color': '#1e40af',
            'accent_color': '#3b82f6',
            'login_background': '',
            'email_from_name': '',
            'email_signature': '',
            'custom_domain': '',
            'enable_white_label': False,
        })
        assert form.is_valid(), form.errors

    def test_no_tenant_field(self):
        assert 'tenant' not in BrandingForm().fields
