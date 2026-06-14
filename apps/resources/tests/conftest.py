"""Shared pytest fixtures for the resources app test suite."""
import datetime
from decimal import Decimal

import pytest
from django.test import Client

from apps.accounts.models import User
from apps.core.models import Tenant
from apps.resources.models import (
    Allocation,
    DemandForecast,
    Resource,
    Skill,
    TeamAssignment,
    TimeEntry,
)


# ---------------------------------------------------------------------------
# Tenants
# ---------------------------------------------------------------------------
@pytest.fixture
def acme_tenant(db):
    """Primary test tenant (Acme Corp)."""
    return Tenant.objects.create(name='Acme Corp', slug='acme', subdomain='acme')


@pytest.fixture
def globex_tenant(db):
    """Secondary test tenant for isolation checks (Globex)."""
    return Tenant.objects.create(name='Globex Inc', slug='globex', subdomain='globex')


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------
@pytest.fixture
def acme_skill(db, acme_tenant):
    """A Skill belonging to Acme."""
    return Skill.objects.create(
        tenant=acme_tenant,
        name='Python',
        category='technical',
        description='Python programming language',
    )


@pytest.fixture
def globex_skill(db, globex_tenant):
    """A Skill belonging to Globex (used in isolation tests)."""
    return Skill.objects.create(
        tenant=globex_tenant,
        name='Java',
        category='technical',
        description='Java programming language',
    )


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------
@pytest.fixture
def acme_resource(db, acme_tenant, acme_admin):
    """A Resource with a linked user belonging to Acme."""
    return Resource.objects.create(
        tenant=acme_tenant,
        name='Alice Engineer',
        resource_type='employee',
        email='alice@acme.test',
        job_title='Software Engineer',
        department='Engineering',
        capacity_hours_per_week=40,
        cost_rate=Decimal('75.00'),
        user=acme_admin,
        is_active=True,
    )


@pytest.fixture
def acme_resource_no_user(db, acme_tenant):
    """A Resource with user=None (contractor without linked account)."""
    return Resource.objects.create(
        tenant=acme_tenant,
        name='Bob Contractor',
        resource_type='contractor',
        email='bob@external.test',
        job_title='Freelance Dev',
        capacity_hours_per_week=20,
        cost_rate=Decimal('100.00'),
        user=None,
        is_active=True,
    )


@pytest.fixture
def globex_resource(db, globex_tenant):
    """A Resource belonging to Globex (used in isolation tests)."""
    return Resource.objects.create(
        tenant=globex_tenant,
        name='Globex Worker',
        resource_type='employee',
        is_active=True,
    )


# ---------------------------------------------------------------------------
# Allocations
# ---------------------------------------------------------------------------
@pytest.fixture
def acme_allocation(db, acme_tenant, acme_resource):
    """An Allocation belonging to Acme."""
    return Allocation.objects.create(
        tenant=acme_tenant,
        resource=acme_resource,
        allocation_percent=80,
        allocated_hours=Decimal('32.00'),
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 3, 31),
        status='planned',
    )


@pytest.fixture
def globex_allocation(db, globex_tenant, globex_resource):
    """An Allocation belonging to Globex."""
    return Allocation.objects.create(
        tenant=globex_tenant,
        resource=globex_resource,
        allocation_percent=100,
        status='active',
    )


# ---------------------------------------------------------------------------
# Team Assignments
# ---------------------------------------------------------------------------
@pytest.fixture
def acme_assignment(db, acme_tenant, acme_resource):
    """A TeamAssignment belonging to Acme."""
    return TeamAssignment.objects.create(
        tenant=acme_tenant,
        resource=acme_resource,
        role_on_project='Lead Developer',
        is_lead=True,
        status='active',
    )


@pytest.fixture
def globex_assignment(db, globex_tenant, globex_resource):
    """A TeamAssignment belonging to Globex."""
    return TeamAssignment.objects.create(
        tenant=globex_tenant,
        resource=globex_resource,
        role_on_project='QA Engineer',
        status='proposed',
    )


# ---------------------------------------------------------------------------
# Demand Forecasts
# ---------------------------------------------------------------------------
@pytest.fixture
def acme_forecast(db, acme_tenant, acme_skill):
    """A DemandForecast belonging to Acme."""
    return DemandForecast.objects.create(
        tenant=acme_tenant,
        title='Q3 Python Demand',
        skill=acme_skill,
        period='2026-07',
        demand_hours=Decimal('160.00'),
        capacity_hours=Decimal('120.00'),
        status='projected',
    )


@pytest.fixture
def globex_forecast(db, globex_tenant):
    """A DemandForecast belonging to Globex."""
    return DemandForecast.objects.create(
        tenant=globex_tenant,
        title='Globex Q4 Demand',
        period='2026-10',
        demand_hours=Decimal('200.00'),
        capacity_hours=Decimal('200.00'),
        status='projected',
    )


# ---------------------------------------------------------------------------
# Time Entries
# ---------------------------------------------------------------------------
@pytest.fixture
def acme_time_entry(db, acme_tenant, acme_resource):
    """A TimeEntry belonging to Acme."""
    return TimeEntry.objects.create(
        tenant=acme_tenant,
        resource=acme_resource,
        work_date=datetime.date(2026, 6, 1),
        hours=Decimal('8.00'),
        is_billable=True,
        status='draft',
        description='Development work',
    )


@pytest.fixture
def globex_time_entry(db, globex_tenant, globex_resource):
    """A TimeEntry belonging to Globex."""
    return TimeEntry.objects.create(
        tenant=globex_tenant,
        resource=globex_resource,
        work_date=datetime.date(2026, 6, 2),
        hours=Decimal('4.00'),
        status='submitted',
    )
