"""Tests for auth, permission, and multi-tenant isolation in the tenants app."""
import datetime

import pytest
from django.urls import reverse

from apps.tenants.models import Invoice, PaymentMethod, Plan, SystemAlert


# ---------------------------------------------------------------------------
# Anonymous user redirects
# ---------------------------------------------------------------------------
PROTECTED_URLS = [
    ('tenants:plan_list', []),
    ('tenants:plan_create', []),
    ('tenants:invoice_list', []),
    ('tenants:invoice_create', []),
    ('tenants:payment_method_list', []),
    ('tenants:payment_method_create', []),
    ('tenants:subscription', []),
    ('tenants:onboarding', []),
    ('tenants:branding', []),
    ('tenants:health', []),
    ('tenants:usage_list', []),
    ('tenants:isolation_security', []),
]


@pytest.mark.parametrize('url_name,args', PROTECTED_URLS)
@pytest.mark.django_db
def test_anonymous_redirected_to_login(anon_client, url_name, args):
    url = reverse(url_name, args=args)
    r = anon_client.get(url)
    assert r.status_code in (302, 301), f"Expected redirect for {url_name}, got {r.status_code}"
    location = r['Location']
    # Django LOGIN_URL is set to 'accounts:login' → resolves to /login/
    assert '/login/' in location or 'login' in location


@pytest.mark.django_db
def test_anonymous_invoice_detail_redirects(anon_client, acme_invoice):
    url = reverse('tenants:invoice_detail', args=[acme_invoice.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_plan_delete_redirects(anon_client, basic_plan):
    url = reverse('tenants:plan_delete', args=[basic_plan.pk])
    r = anon_client.post(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


# ---------------------------------------------------------------------------
# Multi-tenant isolation: invoice
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestInvoiceIsolation:
    def test_acme_cannot_see_globex_invoice_detail(self, acme_client, globex_invoice):
        """Acme client requesting a Globex invoice by PK must get 404."""
        url = reverse('tenants:invoice_detail', args=[globex_invoice.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_invoice(self, acme_client, globex_invoice):
        url = reverse('tenants:invoice_edit', args=[globex_invoice.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_invoice(self, acme_client, globex_invoice):
        url = reverse('tenants:invoice_delete', args=[globex_invoice.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert Invoice.objects.filter(pk=globex_invoice.pk).exists()

    def test_acme_cannot_mark_paid_globex_invoice(self, acme_client, globex_invoice):
        url = reverse('tenants:invoice_mark_paid', args=[globex_invoice.pk])
        r = acme_client.post(url)
        assert r.status_code == 404

    def test_invoice_list_excludes_globex_rows(self, acme_client, acme_invoice, globex_invoice):
        """Acme's invoice list must not contain Globex invoices."""
        url = reverse('tenants:invoice_list')
        r = acme_client.get(url)
        pks = [inv.pk for inv in r.context['invoices']]
        assert acme_invoice.pk in pks
        assert globex_invoice.pk not in pks

    def test_globex_cannot_see_acme_invoice(self, globex_client, acme_invoice):
        url = reverse('tenants:invoice_detail', args=[acme_invoice.pk])
        r = globex_client.get(url)
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Multi-tenant isolation: payment methods
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPaymentMethodIsolation:
    def test_acme_cannot_edit_globex_payment_method(self, acme_client, globex_payment_method):
        url = reverse('tenants:payment_method_edit', args=[globex_payment_method.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_payment_method(self, acme_client, globex_payment_method):
        url = reverse('tenants:payment_method_delete', args=[globex_payment_method.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert PaymentMethod.objects.filter(pk=globex_payment_method.pk).exists()

    def test_acme_cannot_set_default_globex_payment_method(self, acme_client, globex_payment_method):
        url = reverse('tenants:payment_method_set_default', args=[globex_payment_method.pk])
        r = acme_client.post(url)
        assert r.status_code == 404

    def test_payment_method_list_excludes_globex(self, acme_client, acme_payment_method, globex_payment_method):
        url = reverse('tenants:payment_method_list')
        r = acme_client.get(url)
        pks = [pm.pk for pm in r.context['payment_methods']]
        assert acme_payment_method.pk in pks
        assert globex_payment_method.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: alerts
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAlertIsolation:
    def test_acme_cannot_resolve_globex_alert(self, acme_client, globex_tenant):
        alert = SystemAlert.objects.create(
            tenant=globex_tenant,
            title='Globex alert',
            severity='info',
            category='usage',
        )
        url = reverse('tenants:alert_resolve', args=[alert.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        alert.refresh_from_db()
        assert alert.is_resolved is False


# ---------------------------------------------------------------------------
# Plan permission gate (_can_manage_plans)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPlanPermissionGate:
    """Only is_staff or is_tenant_admin users can create/edit/delete plans."""

    def test_staff_user_can_create_plan(self, db):
        """A staff user (is_staff=True, no tenant) can create plans."""
        from django.test import Client
        from apps.accounts.models import User
        staff = User.objects.create_user(
            username='staffuser', password='pass', is_staff=True
        )
        c = Client()
        c.force_login(staff)
        url = reverse('tenants:plan_create')
        r = c.post(url, {
            'name': 'Staff Plan',
            'slug': 'staff-plan',
            'price_monthly': '0',
            'price_yearly': '0',
            'max_users': '5',
            'max_projects': '10',
            'max_storage_gb': '5',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
            'features_text': '',
        })
        assert r.status_code == 302
        assert Plan.objects.filter(slug='staff-plan').exists()

    def test_regular_user_blocked_from_plan_create(self, acme_user_client):
        url = reverse('tenants:plan_create')
        r = acme_user_client.get(url)
        # Should redirect to plan_list with an error message (not 200 form)
        assert r.status_code == 302

    def test_admin_user_can_delete_plan(self, acme_client, basic_plan):
        url = reverse('tenants:plan_delete', args=[basic_plan.pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not Plan.objects.filter(pk=basic_plan.pk).exists()

    def test_regular_user_cannot_delete_plan(self, acme_user_client, basic_plan):
        url = reverse('tenants:plan_delete', args=[basic_plan.pk])
        r = acme_user_client.post(url)
        assert r.status_code == 302
        assert Plan.objects.filter(pk=basic_plan.pk).exists()


# ---------------------------------------------------------------------------
# CSRF enforcement
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestCSRFEnforcement:
    def test_csrf_required_on_invoice_create(self, acme_tenant, acme_admin):
        """POST without CSRF token must be rejected (403)."""
        from django.test import Client
        # Use a client with CSRF enforcement enabled (enforce_csrf_checks=True)
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('tenants:invoice_create')
        r = c.post(url, {
            'subscription': '',
            'amount': '50.00',
            'tax': '0',
            'status': Invoice.STATUS_DRAFT,
            'issue_date': '2025-01-01',
            'due_date': '2025-01-31',
            'notes': '',
        })
        assert r.status_code == 403

    def test_csrf_required_on_plan_create(self, acme_admin):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('tenants:plan_create')
        r = c.post(url, {
            'name': 'Injected',
            'slug': 'injected',
            'price_monthly': '0',
            'price_yearly': '0',
            'max_users': '5',
            'max_projects': '10',
            'max_storage_gb': '5',
            'is_active': True,
            'is_popular': False,
            'sort_order': '0',
        })
        assert r.status_code == 403

    def test_csrf_required_on_invoice_delete(self, acme_admin, acme_invoice):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('tenants:invoice_delete', args=[acme_invoice.pk])
        r = c.post(url)
        assert r.status_code == 403

    def test_csrf_required_on_mark_paid(self, acme_admin, acme_invoice):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('tenants:invoice_mark_paid', args=[acme_invoice.pk])
        r = c.post(url)
        assert r.status_code == 403


# ---------------------------------------------------------------------------
# Globex client list isolation (belt-and-suspenders)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_globex_invoice_list_excludes_acme(globex_client, acme_invoice, globex_invoice):
    url = reverse('tenants:invoice_list')
    r = globex_client.get(url)
    pks = [inv.pk for inv in r.context['invoices']]
    assert globex_invoice.pk in pks
    assert acme_invoice.pk not in pks
