"""Tests for tenants app views: CRUD, context keys, templates, pagination."""
import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.tenants.models import (
    BrandingSettings,
    Invoice,
    PaymentMethod,
    Plan,
    Subscription,
    SystemAlert,
    UsageMetric,
)


# ---------------------------------------------------------------------------
# Plan views
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPlanListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('tenants:plan_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('tenants:plan_list')
        r = acme_client.get(url)
        assert 'tenants/plan_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client, basic_plan):
        url = reverse('tenants:plan_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'plans' in r.context
        assert 'can_manage' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, db, acme_client, basic_plan, pro_plan):
        url = reverse('tenants:plan_list')
        r = acme_client.get(url, {'q': 'Basic'})
        assert r.status_code == 200
        plan_names = [p.name for p in r.context['plans']]
        assert 'Basic' in plan_names
        assert 'Pro' not in plan_names

    def test_status_filter_active(self, db, acme_client, basic_plan):
        Plan.objects.create(name='Inactive Plan', slug='inactive-plan', is_active=False)
        url = reverse('tenants:plan_list')
        r = acme_client.get(url, {'status': 'active'})
        for p in r.context['plans']:
            assert p.is_active is True

    def test_status_filter_inactive(self, db, acme_client, basic_plan):
        Plan.objects.create(name='Old Plan', slug='old-plan', is_active=False)
        url = reverse('tenants:plan_list')
        r = acme_client.get(url, {'status': 'inactive'})
        for p in r.context['plans']:
            assert p.is_active is False

    def test_pagination_size_10(self, db, acme_client):
        for i in range(15):
            Plan.objects.create(name=f'Plan {i:02d}', slug=f'plan-{i:02d}', is_active=True)
        url = reverse('tenants:plan_list')
        r = acme_client.get(url)
        assert len(r.context['plans']) <= 10

    def test_can_manage_true_for_admin(self, acme_client):
        url = reverse('tenants:plan_list')
        r = acme_client.get(url)
        assert r.context['can_manage'] is True

    def test_can_manage_false_for_regular_user(self, acme_user_client):
        url = reverse('tenants:plan_list')
        r = acme_user_client.get(url)
        assert r.context['can_manage'] is False


@pytest.mark.django_db
class TestPlanCreateView:
    def test_admin_can_get_form(self, acme_client):
        url = reverse('tenants:plan_create')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_admin_can_create_plan(self, db, acme_client):
        url = reverse('tenants:plan_create')
        r = acme_client.post(url, {
            'name': 'Enterprise',
            'slug': 'enterprise',
            'price_monthly': '99.99',
            'price_yearly': '999.99',
            'max_users': '100',
            'max_projects': '1000',
            'max_storage_gb': '500',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
            'features_text': 'All features',
        })
        assert r.status_code == 302
        assert Plan.objects.filter(slug='enterprise').exists()

    def test_non_admin_redirected(self, acme_user_client):
        url = reverse('tenants:plan_create')
        r = acme_user_client.post(url, {
            'name': 'Hacked',
            'slug': 'hacked',
            'price_monthly': '0',
            'price_yearly': '0',
            'max_users': '999',
            'max_projects': '999',
            'max_storage_gb': '999',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
        })
        assert r.status_code == 302
        assert not Plan.objects.filter(slug='hacked').exists()


@pytest.mark.django_db
class TestPlanEditView:
    def test_admin_can_edit_plan(self, db, acme_client, basic_plan):
        url = reverse('tenants:plan_edit', args=[basic_plan.pk])
        r = acme_client.post(url, {
            'name': 'Basic Updated',
            'slug': 'basic',
            'price_monthly': '12.99',
            'price_yearly': '129.99',
            'max_users': '5',
            'max_projects': '10',
            'max_storage_gb': '5',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
            'features_text': '',
        })
        assert r.status_code == 302
        basic_plan.refresh_from_db()
        assert basic_plan.name == 'Basic Updated'

    def test_non_admin_cannot_edit(self, acme_user_client, basic_plan):
        url = reverse('tenants:plan_edit', args=[basic_plan.pk])
        r = acme_user_client.post(url, {
            'name': 'Hacked',
            'slug': 'basic',
            'price_monthly': '0',
            'price_yearly': '0',
            'max_users': '999',
            'max_projects': '999',
            'max_storage_gb': '999',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
        })
        assert r.status_code == 302
        basic_plan.refresh_from_db()
        assert basic_plan.name == 'Basic'  # unchanged


@pytest.mark.django_db
class TestPlanDeleteView:
    def test_admin_can_delete(self, db, acme_client, basic_plan):
        url = reverse('tenants:plan_delete', args=[basic_plan.pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not Plan.objects.filter(pk=basic_plan.pk).exists()

    def test_non_admin_cannot_delete(self, acme_user_client, basic_plan):
        url = reverse('tenants:plan_delete', args=[basic_plan.pk])
        r = acme_user_client.post(url)
        assert r.status_code == 302
        assert Plan.objects.filter(pk=basic_plan.pk).exists()

    def test_get_request_redirects(self, acme_client, basic_plan):
        """DELETE view must be POST-only; GET just redirects."""
        url = reverse('tenants:plan_delete', args=[basic_plan.pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert Plan.objects.filter(pk=basic_plan.pk).exists()


# ---------------------------------------------------------------------------
# Invoice views
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestInvoiceListView:
    def test_200_for_logged_in(self, acme_client, acme_invoice):
        url = reverse('tenants:invoice_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client, acme_invoice):
        url = reverse('tenants:invoice_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'invoices' in r.context
        assert 'status_choices' in r.context
        assert 'total_count' in r.context

    def test_template_used(self, acme_client):
        url = reverse('tenants:invoice_list')
        r = acme_client.get(url)
        assert 'tenants/invoice_list.html' in [t.name for t in r.templates]

    def test_search_by_number(self, acme_client, acme_invoice):
        url = reverse('tenants:invoice_list')
        r = acme_client.get(url, {'q': acme_invoice.number})
        assert acme_invoice in list(r.context['invoices'])

    def test_status_filter(self, db, acme_client, acme_tenant, acme_invoice):
        # Create a paid invoice
        paid = Invoice.objects.create(
            tenant=acme_tenant,
            amount=Decimal('50'),
            status=Invoice.STATUS_PAID,
            issue_date=datetime.date.today(),
            due_date=datetime.date.today(),
        )
        url = reverse('tenants:invoice_list')
        r = acme_client.get(url, {'status': 'paid'})
        invoices = list(r.context['invoices'])
        assert paid in invoices
        assert acme_invoice not in invoices

    def test_pagination_size_10(self, db, acme_client, acme_tenant):
        for i in range(15):
            Invoice.objects.create(
                tenant=acme_tenant,
                amount=Decimal(str(i + 1)),
                issue_date=datetime.date.today(),
                due_date=datetime.date.today(),
            )
        url = reverse('tenants:invoice_list')
        r = acme_client.get(url)
        assert len(r.context['invoices']) <= 10


@pytest.mark.django_db
class TestInvoiceCreateView:
    def test_get_form(self, acme_client):
        url = reverse('tenants:invoice_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_invoice_with_correct_tenant(self, acme_client, acme_tenant):
        count_before = Invoice.objects.filter(tenant=acme_tenant).count()
        url = reverse('tenants:invoice_create')
        r = acme_client.post(url, {
            'subscription': '',
            'amount': '150.00',
            'tax': '15.00',
            'status': Invoice.STATUS_DRAFT,
            'issue_date': '2025-06-01',
            'due_date': '2025-06-30',
            'notes': 'Test invoice',
        })
        assert r.status_code == 302
        assert Invoice.objects.filter(tenant=acme_tenant).count() == count_before + 1
        inv = Invoice.objects.filter(tenant=acme_tenant).order_by('-id').first()
        assert inv.amount.__float__() == pytest.approx(150.00)
        assert inv.number.startswith('INV-')

    def test_post_does_not_create_for_other_tenant(self, acme_client, globex_tenant):
        url = reverse('tenants:invoice_create')
        acme_client.post(url, {
            'subscription': '',
            'amount': '50.00',
            'tax': '0',
            'status': Invoice.STATUS_DRAFT,
            'issue_date': '2025-06-01',
            'due_date': '2025-06-30',
            'notes': '',
        })
        # Globex should have no invoices from Acme's POST
        assert Invoice.objects.filter(tenant=globex_tenant).count() == 0


@pytest.mark.django_db
class TestInvoiceDetailView:
    def test_200_for_owner(self, acme_client, acme_invoice):
        url = reverse('tenants:invoice_detail', args=[acme_invoice.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'invoice' in r.context
        assert r.context['invoice'].pk == acme_invoice.pk


@pytest.mark.django_db
class TestInvoiceEditView:
    def test_edit_updates_invoice(self, acme_client, acme_invoice):
        url = reverse('tenants:invoice_edit', args=[acme_invoice.pk])
        r = acme_client.post(url, {
            'subscription': '',
            'amount': '200.00',
            'tax': '20.00',
            'status': Invoice.STATUS_SENT,
            'issue_date': '2025-01-01',
            'due_date': '2025-01-31',
            'notes': 'Updated',
        })
        assert r.status_code == 302
        acme_invoice.refresh_from_db()
        assert acme_invoice.status == Invoice.STATUS_SENT

    def test_get_edit_form(self, acme_client, acme_invoice):
        url = reverse('tenants:invoice_edit', args=[acme_invoice.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'invoice' in r.context


@pytest.mark.django_db
class TestInvoiceDeleteView:
    def test_post_deletes_invoice(self, acme_client, acme_invoice):
        pk = acme_invoice.pk
        url = reverse('tenants:invoice_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not Invoice.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_invoice):
        pk = acme_invoice.pk
        url = reverse('tenants:invoice_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert Invoice.objects.filter(pk=pk).exists()


@pytest.mark.django_db
class TestInvoiceMarkPaidView:
    def test_mark_paid(self, acme_client, acme_invoice):
        url = reverse('tenants:invoice_mark_paid', args=[acme_invoice.pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        acme_invoice.refresh_from_db()
        assert acme_invoice.status == Invoice.STATUS_PAID
        assert acme_invoice.paid_at == datetime.date.today()

    def test_get_does_not_mark_paid(self, acme_client, acme_invoice):
        url = reverse('tenants:invoice_mark_paid', args=[acme_invoice.pk])
        acme_client.get(url)
        acme_invoice.refresh_from_db()
        assert acme_invoice.status == Invoice.STATUS_DRAFT


# ---------------------------------------------------------------------------
# Payment method views
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPaymentMethodListView:
    def test_200(self, acme_client):
        url = reverse('tenants:payment_method_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client, acme_payment_method):
        url = reverse('tenants:payment_method_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'payment_methods' in r.context
        assert 'total_count' in r.context

    def test_pagination_size_10(self, db, acme_client, acme_tenant):
        for i in range(15):
            PaymentMethod.objects.create(
                tenant=acme_tenant,
                type='card',
                last4=str(i).zfill(4),
            )
        url = reverse('tenants:payment_method_list')
        r = acme_client.get(url)
        assert len(r.context['payment_methods']) <= 10


@pytest.mark.django_db
class TestPaymentMethodCreateView:
    def test_create(self, acme_client, acme_tenant):
        url = reverse('tenants:payment_method_create')
        r = acme_client.post(url, {
            'type': 'card',
            'brand': 'Visa',
            'last4': '1234',
            'exp_month': '12',
            'exp_year': '2029',
            'holder_name': 'Acme Admin',
            'is_default': True,
        })
        assert r.status_code == 302
        assert PaymentMethod.objects.filter(tenant=acme_tenant, last4='1234').exists()

    def test_is_default_clears_others(self, db, acme_client, acme_tenant, acme_payment_method):
        """When a new default is set, old default should be cleared."""
        assert acme_payment_method.is_default is True
        url = reverse('tenants:payment_method_create')
        acme_client.post(url, {
            'type': 'bank',
            'brand': 'Chase',
            'last4': '9999',
            'exp_month': '',
            'exp_year': '',
            'holder_name': '',
            'is_default': True,
        })
        acme_payment_method.refresh_from_db()
        assert acme_payment_method.is_default is False


@pytest.mark.django_db
class TestPaymentMethodDeleteView:
    def test_post_deletes(self, acme_client, acme_payment_method):
        pk = acme_payment_method.pk
        url = reverse('tenants:payment_method_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not PaymentMethod.objects.filter(pk=pk).exists()


# ---------------------------------------------------------------------------
# Subscription view
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSubscriptionView:
    def test_200(self, acme_client, acme_subscription, basic_plan):
        url = reverse('tenants:subscription')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client, acme_subscription, basic_plan):
        url = reverse('tenants:subscription')
        r = acme_client.get(url)
        assert 'subscription' in r.context
        assert 'plans' in r.context
        assert 'payment_methods' in r.context
        assert 'recent_invoices' in r.context

    def test_post_changes_plan(self, acme_client, acme_subscription, pro_plan):
        url = reverse('tenants:subscription')
        r = acme_client.post(url, {'plan': str(pro_plan.pk), 'billing_cycle': 'yearly'})
        assert r.status_code == 302
        acme_subscription.refresh_from_db()
        assert acme_subscription.plan == pro_plan
        assert acme_subscription.billing_cycle == 'yearly'


# ---------------------------------------------------------------------------
# Onboarding view
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestOnboardingView:
    def test_200(self, acme_client, acme_tenant):
        url = reverse('tenants:onboarding')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client, acme_tenant):
        url = reverse('tenants:onboarding')
        r = acme_client.get(url)
        assert 'form' in r.context
        assert 'tenant' in r.context
        assert 'branding' in r.context

    def test_post_saves_tenant(self, acme_client, acme_tenant):
        url = reverse('tenants:onboarding')
        r = acme_client.post(url, {
            'name': 'Acme Corp Updated',
            'subdomain': 'acme',
            'contact_email': 'new@acme.test',
            'is_active': True,
        })
        assert r.status_code == 302
        acme_tenant.refresh_from_db()
        assert acme_tenant.name == 'Acme Corp Updated'


# ---------------------------------------------------------------------------
# Branding view
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestBrandingView:
    def test_200(self, acme_client, acme_tenant):
        url = reverse('tenants:branding')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client, acme_tenant):
        url = reverse('tenants:branding')
        r = acme_client.get(url)
        assert 'form' in r.context
        assert 'branding' in r.context
        assert 'tenant' in r.context

    def test_post_saves_branding(self, acme_client, acme_tenant):
        url = reverse('tenants:branding')
        r = acme_client.post(url, {
            'primary_color': '#ff0000',
            'secondary_color': '#1e40af',
            'accent_color': '#3b82f6',
            'login_background': '',
            'email_from_name': 'Acme',
            'email_signature': '',
            'custom_domain': '',
            'enable_white_label': False,
        })
        assert r.status_code == 302
        bs = BrandingSettings.objects.get(tenant=acme_tenant)
        assert bs.primary_color == '#ff0000'


# ---------------------------------------------------------------------------
# Health view
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestHealthView:
    def test_200(self, acme_client, acme_tenant):
        url = reverse('tenants:health')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client, acme_tenant):
        url = reverse('tenants:health')
        r = acme_client.get(url)
        assert 'usage_metrics' in r.context
        assert 'alerts' in r.context
        assert 'open_alerts' in r.context
        assert 'open_alert_count' in r.context


# ---------------------------------------------------------------------------
# Isolation & security view
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestIsolationSecurityView:
    def test_200(self, acme_client, acme_tenant):
        url = reverse('tenants:isolation_security')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client, acme_tenant):
        url = reverse('tenants:isolation_security')
        r = acme_client.get(url)
        assert 'tenant' in r.context
        assert 'security_alerts' in r.context
        assert 'recent_audit' in r.context
        assert 'encryption_at_rest' in r.context
        assert 'encryption_in_transit' in r.context


# ---------------------------------------------------------------------------
# Usage list view
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUsageListView:
    def test_200(self, acme_client, acme_tenant):
        url = reverse('tenants:usage_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client, acme_tenant):
        url = reverse('tenants:usage_list')
        r = acme_client.get(url)
        assert 'usage_metrics' in r.context
        assert 'page_obj' in r.context
        assert 'total_count' in r.context


# ---------------------------------------------------------------------------
# Alert resolve view
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAlertResolveView:
    def test_post_resolves_alert(self, acme_client, acme_tenant):
        alert = SystemAlert.objects.create(
            tenant=acme_tenant,
            severity='warning',
            category='billing',
            title='Test alert',
        )
        url = reverse('tenants:alert_resolve', args=[alert.pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        alert.refresh_from_db()
        assert alert.is_resolved is True
        assert alert.resolved_at is not None

    def test_get_does_not_resolve(self, acme_client, acme_tenant):
        alert = SystemAlert.objects.create(
            tenant=acme_tenant,
            severity='info',
            category='usage',
            title='Not yet resolved',
        )
        url = reverse('tenants:alert_resolve', args=[alert.pk])
        acme_client.get(url)
        alert.refresh_from_db()
        assert alert.is_resolved is False


# ---------------------------------------------------------------------------
# N+1 guard
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_invoice_list_no_n_plus_1(acme_client, acme_tenant, django_assert_max_num_queries):
    """invoice_list should not issue more than ~10 queries regardless of count."""
    for i in range(12):
        Invoice.objects.create(
            tenant=acme_tenant,
            amount=Decimal(str(i + 1)),
            issue_date=datetime.date.today(),
            due_date=datetime.date.today(),
        )
    url = reverse('tenants:invoice_list')
    with django_assert_max_num_queries(10):
        r = acme_client.get(url)
    assert r.status_code == 200


@pytest.mark.django_db
def test_plan_list_no_n_plus_1(acme_client, django_assert_max_num_queries):
    for i in range(12):
        Plan.objects.create(name=f'Plan {i:02d}', slug=f'plan-{i:02d}')
    url = reverse('tenants:plan_list')
    with django_assert_max_num_queries(10):
        r = acme_client.get(url)
    assert r.status_code == 200
