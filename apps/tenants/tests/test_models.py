"""Tests for tenants app models."""
import datetime
from decimal import Decimal

import pytest

from django.utils import timezone

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
# Plan
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPlan:
    def test_str(self):
        plan = Plan(name='Enterprise')
        assert str(plan) == 'Enterprise'

    def test_defaults(self, db):
        plan = Plan.objects.create(name='Starter', slug='starter')
        assert plan.price_monthly == Decimal('0')
        assert plan.price_yearly == Decimal('0')
        assert plan.max_users == 5
        assert plan.max_projects == 10
        assert plan.max_storage_gb == 5
        assert plan.features == []
        assert plan.is_active is True
        assert plan.is_popular is False
        assert plan.sort_order == 0

    def test_slug_unique(self, db):
        Plan.objects.create(name='Basic', slug='basic')
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Plan.objects.create(name='Basic2', slug='basic')

    def test_ordering(self, db):
        Plan.objects.create(name='Z Plan', slug='z-plan', sort_order=2, price_monthly='20')
        Plan.objects.create(name='A Plan', slug='a-plan', sort_order=1, price_monthly='10')
        plans = list(Plan.objects.all())
        assert plans[0].slug == 'a-plan'
        assert plans[1].slug == 'z-plan'

    def test_features_json(self, db):
        plan = Plan.objects.create(name='Pro', slug='pro', features=['SSO', 'API access'])
        plan.refresh_from_db()
        assert plan.features == ['SSO', 'API access']


# ---------------------------------------------------------------------------
# Subscription
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSubscription:
    def test_str(self, acme_subscription, acme_tenant, basic_plan):
        assert 'Acme Corp' in str(acme_subscription)
        assert 'Basic' in str(acme_subscription)
        assert 'active' in str(acme_subscription)

    def test_status_choices(self):
        values = [v for v, _ in Subscription.STATUS_CHOICES]
        assert 'trialing' in values
        assert 'active' in values
        assert 'past_due' in values
        assert 'canceled' in values
        assert 'expired' in values

    def test_billing_choices(self):
        values = [v for v, _ in Subscription.BILLING_CHOICES]
        assert 'monthly' in values
        assert 'yearly' in values

    def test_default_status_is_trialing(self, db, acme_tenant, basic_plan):
        today = datetime.date.today()
        sub = Subscription.objects.create(
            tenant=acme_tenant,
            plan=basic_plan,
            started_at=today,
            current_period_start=today,
            current_period_end=today + datetime.timedelta(days=14),
        )
        assert sub.status == Subscription.STATUS_TRIALING

    def test_is_trial_true(self, db, acme_tenant, basic_plan):
        today = datetime.date.today()
        sub = Subscription.objects.create(
            tenant=acme_tenant,
            plan=basic_plan,
            status=Subscription.STATUS_TRIALING,
            started_at=today,
            current_period_start=today,
            current_period_end=today + datetime.timedelta(days=14),
        )
        assert sub.is_trial() is True

    def test_is_trial_false(self, acme_subscription):
        assert acme_subscription.is_trial() is False

    def test_days_left_active(self, acme_subscription):
        days = acme_subscription.days_left()
        assert isinstance(days, int)
        assert days >= 0

    def test_days_left_trialing(self, db, acme_tenant, basic_plan):
        # Use Django's timezone basis (UTC) to match Subscription.days_left(), which
        # computes timezone.now().date(); datetime.date.today() (local) drifts by a
        # day during the UTC offset window and made this assertion flaky.
        today = timezone.now().date()
        sub = Subscription.objects.create(
            tenant=acme_tenant,
            plan=basic_plan,
            status=Subscription.STATUS_TRIALING,
            trial_ends_at=today + datetime.timedelta(days=7),
            started_at=today,
            current_period_start=today,
            current_period_end=today + datetime.timedelta(days=30),
        )
        assert sub.days_left() == 7

    def test_days_left_no_end(self, db, acme_tenant, basic_plan):
        today = datetime.date.today()
        sub = Subscription.objects.create(
            tenant=acme_tenant,
            plan=basic_plan,
            status=Subscription.STATUS_TRIALING,
            trial_ends_at=None,
            started_at=today,
            current_period_start=today,
            current_period_end=today + datetime.timedelta(days=30),
        )
        assert sub.days_left() == 0

    def test_one_subscription_per_tenant(self, db, acme_tenant, basic_plan, acme_subscription):
        """Second subscription for same tenant raises IntegrityError (OneToOne)."""
        from django.db import IntegrityError
        today = datetime.date.today()
        with pytest.raises(IntegrityError):
            Subscription.objects.create(
                tenant=acme_tenant,
                plan=basic_plan,
                started_at=today,
                current_period_start=today,
                current_period_end=today + datetime.timedelta(days=30),
            )


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestInvoice:
    def test_str_returns_number(self, acme_invoice):
        assert str(acme_invoice) == acme_invoice.number

    def test_number_format(self, acme_invoice):
        """Invoice number must match INV-##### pattern."""
        import re
        assert re.match(r'^INV-\d{5}$', acme_invoice.number)

    def test_auto_number_on_save(self, db, acme_tenant):
        inv = Invoice.objects.create(
            tenant=acme_tenant,
            amount=Decimal('50.00'),
            issue_date=datetime.date.today(),
            due_date=datetime.date.today(),
        )
        assert inv.number.startswith('INV-')
        assert len(inv.number) == 9  # INV-#####

    def test_total_auto_computed(self, db, acme_tenant):
        inv = Invoice.objects.create(
            tenant=acme_tenant,
            amount=Decimal('100.00'),
            tax=Decimal('20.00'),
            issue_date=datetime.date.today(),
            due_date=datetime.date.today(),
        )
        assert inv.total == Decimal('120.00')

    def test_total_not_recomputed_if_already_set(self, db, acme_tenant):
        """If total is passed explicitly, invoice.save() should not override it."""
        inv = Invoice(
            tenant=acme_tenant,
            amount=Decimal('100.00'),
            tax=Decimal('20.00'),
            total=Decimal('999.00'),  # explicit
            issue_date=datetime.date.today(),
            due_date=datetime.date.today(),
        )
        inv.save()
        # The save() only sets total if not self.total (falsy), 999 is truthy
        assert inv.total == Decimal('999.00')

    def test_numbers_are_unique(self, db, acme_tenant, globex_tenant):
        inv1 = Invoice.objects.create(
            tenant=acme_tenant,
            amount=Decimal('10.00'),
            issue_date=datetime.date.today(),
            due_date=datetime.date.today(),
        )
        inv2 = Invoice.objects.create(
            tenant=globex_tenant,
            amount=Decimal('20.00'),
            issue_date=datetime.date.today(),
            due_date=datetime.date.today(),
        )
        assert inv1.number != inv2.number

    def test_status_choices(self):
        values = [v for v, _ in Invoice.STATUS_CHOICES]
        assert 'draft' in values
        assert 'sent' in values
        assert 'paid' in values
        assert 'overdue' in values
        assert 'void' in values

    def test_default_status_is_draft(self, db, acme_tenant):
        inv = Invoice.objects.create(
            tenant=acme_tenant,
            amount=Decimal('50.00'),
            issue_date=datetime.date.today(),
            due_date=datetime.date.today(),
        )
        assert inv.status == Invoice.STATUS_DRAFT

    def test_ordering(self, db, acme_tenant):
        inv1 = Invoice.objects.create(
            tenant=acme_tenant,
            amount=Decimal('10'),
            issue_date=datetime.date(2025, 1, 1),
            due_date=datetime.date(2025, 1, 31),
        )
        inv2 = Invoice.objects.create(
            tenant=acme_tenant,
            amount=Decimal('20'),
            issue_date=datetime.date(2025, 3, 1),
            due_date=datetime.date(2025, 3, 31),
        )
        qs = list(Invoice.objects.all())
        # Most recent issue_date first
        assert qs[0].id == inv2.id


# ---------------------------------------------------------------------------
# PaymentMethod
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPaymentMethod:
    def test_str(self, acme_payment_method):
        s = str(acme_payment_method)
        assert '4242' in s
        assert 'Card' in s or 'card' in s.lower()

    def test_type_choices(self):
        values = [v for v, _ in PaymentMethod.TYPE_CHOICES]
        assert 'card' in values
        assert 'bank' in values
        assert 'paypal' in values

    def test_defaults(self, db, acme_tenant):
        pm = PaymentMethod.objects.create(tenant=acme_tenant)
        assert pm.type == 'card'
        assert pm.is_default is False

    def test_str_no_last4(self, db, acme_tenant):
        pm = PaymentMethod.objects.create(tenant=acme_tenant, type='paypal')
        # Should not crash even with empty last4
        s = str(pm)
        assert isinstance(s, str)


# ---------------------------------------------------------------------------
# UsageMetric
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUsageMetric:
    def test_str(self, db, acme_tenant):
        um = UsageMetric.objects.create(
            tenant=acme_tenant,
            metric='users',
            value=Decimal('3'),
            limit=Decimal('5'),
        )
        s = str(um)
        assert 'Users' in s
        assert '3' in s
        assert '5' in s

    def test_percent_normal(self, db, acme_tenant):
        um = UsageMetric.objects.create(
            tenant=acme_tenant,
            metric='users',
            value=Decimal('3'),
            limit=Decimal('5'),
        )
        assert um.percent() == 60

    def test_percent_zero_limit(self, db, acme_tenant):
        um = UsageMetric.objects.create(
            tenant=acme_tenant,
            metric='storage',
            value=Decimal('100'),
            limit=Decimal('0'),
        )
        assert um.percent() == 0

    def test_percent_capped_at_100(self, db, acme_tenant):
        um = UsageMetric.objects.create(
            tenant=acme_tenant,
            metric='projects',
            value=Decimal('200'),
            limit=Decimal('10'),
        )
        assert um.percent() == 100

    def test_metric_choices(self):
        values = [v for v, _ in UsageMetric.METRIC_CHOICES]
        assert 'users' in values
        assert 'storage' in values
        assert 'api_calls' in values
        assert 'projects' in values


# ---------------------------------------------------------------------------
# BrandingSettings
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestBrandingSettings:
    def test_str(self, db, acme_tenant):
        bs = BrandingSettings.objects.create(tenant=acme_tenant)
        assert 'Acme Corp' in str(bs)

    def test_defaults(self, db, acme_tenant):
        bs = BrandingSettings.objects.create(tenant=acme_tenant)
        assert bs.primary_color == '#2563eb'
        assert bs.secondary_color == '#1e40af'
        assert bs.accent_color == '#3b82f6'
        assert bs.enable_white_label is False

    def test_one_to_one_per_tenant(self, db, acme_tenant):
        BrandingSettings.objects.create(tenant=acme_tenant)
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            BrandingSettings.objects.create(tenant=acme_tenant)


# ---------------------------------------------------------------------------
# SystemAlert
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSystemAlert:
    def test_str(self, db, acme_tenant):
        alert = SystemAlert.objects.create(
            tenant=acme_tenant,
            severity='warning',
            category='billing',
            title='Payment overdue',
        )
        assert '[warning]' in str(alert)
        assert 'Payment overdue' in str(alert)

    def test_severity_choices(self):
        values = [v for v, _ in SystemAlert.SEVERITY_CHOICES]
        assert 'info' in values
        assert 'warning' in values
        assert 'critical' in values

    def test_category_choices(self):
        values = [v for v, _ in SystemAlert.CATEGORY_CHOICES]
        assert 'security' in values
        assert 'performance' in values
        assert 'billing' in values
        assert 'usage' in values

    def test_defaults(self, db, acme_tenant):
        alert = SystemAlert.objects.create(
            tenant=acme_tenant,
            title='Test alert',
        )
        assert alert.severity == 'info'
        assert alert.category == 'usage'
        assert alert.is_resolved is False
        assert alert.resolved_at is None

    def test_ordering_newest_first(self, db, acme_tenant):
        from django.utils import timezone
        import time
        a1 = SystemAlert.objects.create(tenant=acme_tenant, title='First')
        time.sleep(0.01)
        a2 = SystemAlert.objects.create(tenant=acme_tenant, title='Second')
        alerts = list(SystemAlert.objects.filter(tenant=acme_tenant))
        assert alerts[0].id == a2.id  # newest first
