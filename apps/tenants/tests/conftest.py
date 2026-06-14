"""Shared pytest fixtures for the tenants app test suite."""
import datetime

import pytest
from django.test import Client

from apps.accounts.models import Role, User
from apps.core.models import Tenant


@pytest.fixture
def acme_tenant(db):
    """Primary test tenant (Acme Corp)."""
    return Tenant.objects.create(name='Acme Corp', slug='acme', subdomain='acme')


@pytest.fixture
def globex_tenant(db):
    """Secondary test tenant for isolation checks (Globex)."""
    return Tenant.objects.create(name='Globex Inc', slug='globex', subdomain='globex')


@pytest.fixture
def acme_role(db, acme_tenant):
    """A Role scoped to Acme."""
    return Role.objects.create(tenant=acme_tenant, name='Member')


@pytest.fixture
def globex_role(db, globex_tenant):
    """A Role scoped to Globex."""
    return Role.objects.create(tenant=globex_tenant, name='Member')


@pytest.fixture
def acme_admin(db, acme_tenant):
    """Tenant admin user for Acme Corp."""
    return User.objects.create_user(
        username='acme_admin',
        password='testpass123',
        tenant=acme_tenant,
        is_tenant_admin=True,
        email='admin@acme.test',
    )


@pytest.fixture
def acme_user(db, acme_tenant):
    """Non-admin tenant user for Acme Corp."""
    return User.objects.create_user(
        username='acme_user',
        password='testpass123',
        tenant=acme_tenant,
        is_tenant_admin=False,
        email='user@acme.test',
    )


@pytest.fixture
def globex_admin(db, globex_tenant):
    """Tenant admin user for Globex Inc."""
    return User.objects.create_user(
        username='globex_admin',
        password='testpass123',
        tenant=globex_tenant,
        is_tenant_admin=True,
        email='admin@globex.test',
    )


@pytest.fixture
def acme_client(db, acme_admin):
    """Django test Client pre-logged-in as the Acme tenant admin."""
    c = Client()
    c.force_login(acme_admin)
    return c


@pytest.fixture
def acme_user_client(db, acme_user):
    """Django test Client logged in as a non-admin Acme user."""
    c = Client()
    c.force_login(acme_user)
    return c


@pytest.fixture
def globex_client(db, globex_admin):
    """Django test Client pre-logged-in as the Globex tenant admin."""
    c = Client()
    c.force_login(globex_admin)
    return c


@pytest.fixture
def anon_client():
    """Unauthenticated Django test Client."""
    return Client()


@pytest.fixture
def basic_plan(db):
    """A simple active subscription Plan."""
    from apps.tenants.models import Plan
    return Plan.objects.create(
        name='Basic',
        slug='basic',
        price_monthly='9.99',
        price_yearly='99.99',
        max_users=5,
        max_projects=10,
        is_active=True,
    )


@pytest.fixture
def pro_plan(db):
    """A second active subscription Plan."""
    from apps.tenants.models import Plan
    return Plan.objects.create(
        name='Pro',
        slug='pro',
        price_monthly='29.99',
        price_yearly='299.99',
        max_users=25,
        max_projects=100,
        is_active=True,
        is_popular=True,
    )


@pytest.fixture
def acme_subscription(db, acme_tenant, basic_plan):
    """An active subscription for Acme Corp."""
    from apps.tenants.models import Subscription
    today = datetime.date.today()
    return Subscription.objects.create(
        tenant=acme_tenant,
        plan=basic_plan,
        status=Subscription.STATUS_ACTIVE,
        billing_cycle='monthly',
        started_at=today,
        current_period_start=today,
        current_period_end=today + datetime.timedelta(days=30),
    )


@pytest.fixture
def acme_invoice(db, acme_tenant, acme_subscription):
    """A draft Invoice for Acme Corp."""
    from decimal import Decimal
    from apps.tenants.models import Invoice
    return Invoice.objects.create(
        tenant=acme_tenant,
        subscription=acme_subscription,
        amount=Decimal('100.00'),
        tax=Decimal('10.00'),
        issue_date=datetime.date(2025, 1, 1),
        due_date=datetime.date(2025, 1, 31),
    )


@pytest.fixture
def globex_invoice(db, globex_tenant):
    """A draft Invoice for Globex (used in isolation tests)."""
    from decimal import Decimal
    from apps.tenants.models import Invoice
    return Invoice.objects.create(
        tenant=globex_tenant,
        amount=Decimal('200.00'),
        issue_date=datetime.date(2025, 2, 1),
        due_date=datetime.date(2025, 2, 28),
    )


@pytest.fixture
def acme_payment_method(db, acme_tenant):
    """A PaymentMethod for Acme Corp."""
    from apps.tenants.models import PaymentMethod
    return PaymentMethod.objects.create(
        tenant=acme_tenant,
        type='card',
        brand='Visa',
        last4='4242',
        exp_month=12,
        exp_year=2027,
        holder_name='Acme Admin',
        is_default=True,
    )


@pytest.fixture
def globex_payment_method(db, globex_tenant):
    """A PaymentMethod for Globex (used in isolation tests)."""
    from apps.tenants.models import PaymentMethod
    return PaymentMethod.objects.create(
        tenant=globex_tenant,
        type='card',
        brand='Mastercard',
        last4='5555',
        exp_month=6,
        exp_year=2028,
        holder_name='Globex Admin',
        is_default=True,
    )
