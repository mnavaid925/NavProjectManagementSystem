"""Shared pytest fixtures for the initiation app test suite."""
import datetime

import pytest
from django.test import Client

from apps.accounts.models import User
from apps.core.models import Tenant
from apps.initiation.models import (
    BusinessCase,
    KickoffTask,
    ProjectCharter,
    ProjectRequest,
    Stakeholder,
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
    """Tenant admin for Acme Corp."""
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
    """Tenant admin for Globex Inc."""
    return User.objects.create_user(
        username='globex_admin',
        password='testpass123',
        tenant=globex_tenant,
        is_tenant_admin=True,
        email='admin@globex.test',
    )


# ---------------------------------------------------------------------------
# Logged-in clients
# ---------------------------------------------------------------------------

@pytest.fixture
def acme_client(db, acme_admin):
    """Django test Client logged in as the Acme tenant admin."""
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
    """Django test Client logged in as the Globex tenant admin."""
    c = Client()
    c.force_login(globex_admin)
    return c


@pytest.fixture
def anon_client():
    """Unauthenticated Django test Client."""
    return Client()


# ---------------------------------------------------------------------------
# Sample model objects for Acme
# ---------------------------------------------------------------------------

@pytest.fixture
def acme_request(db, acme_tenant):
    """A ProjectRequest belonging to Acme Corp."""
    return ProjectRequest.objects.create(
        tenant=acme_tenant,
        title='Acme Portal Upgrade',
        department='IT',
        description='Upgrade the customer portal.',
        priority='high',
        status='draft',
    )


@pytest.fixture
def acme_business_case(db, acme_tenant, acme_request):
    """A BusinessCase belonging to Acme Corp."""
    return BusinessCase.objects.create(
        tenant=acme_tenant,
        title='Acme Portal BC',
        request=acme_request,
        summary='ROI analysis for the portal upgrade.',
        recommendation='go',
        status='draft',
    )


@pytest.fixture
def acme_charter(db, acme_tenant):
    """A ProjectCharter belonging to Acme Corp."""
    return ProjectCharter.objects.create(
        tenant=acme_tenant,
        title='Acme Portal Charter',
        objectives='Deliver new portal.',
        status='draft',
    )


@pytest.fixture
def acme_stakeholder(db, acme_tenant):
    """A Stakeholder belonging to Acme Corp."""
    return Stakeholder.objects.create(
        tenant=acme_tenant,
        name='Alice Smith',
        organization='Acme Corp',
        role_title='Sponsor',
        email='alice@acme.test',
        influence='high',
        interest='high',
        engagement='supportive',
    )


@pytest.fixture
def acme_kickoff(db, acme_tenant, acme_charter):
    """A KickoffTask belonging to Acme Corp."""
    return KickoffTask.objects.create(
        tenant=acme_tenant,
        title='Book kickoff room',
        charter=acme_charter,
        category='logistics',
        status='pending',
        due_date=datetime.date(2026, 7, 1),
    )


# ---------------------------------------------------------------------------
# Sample model objects for Globex (isolation tests)
# ---------------------------------------------------------------------------

@pytest.fixture
def globex_request(db, globex_tenant):
    """A ProjectRequest belonging to Globex Inc."""
    return ProjectRequest.objects.create(
        tenant=globex_tenant,
        title='Globex ERP Integration',
        department='Finance',
        priority='medium',
        status='submitted',
    )


@pytest.fixture
def globex_business_case(db, globex_tenant):
    """A BusinessCase belonging to Globex Inc."""
    return BusinessCase.objects.create(
        tenant=globex_tenant,
        title='Globex ERP BC',
        recommendation='hold',
        status='draft',
    )


@pytest.fixture
def globex_charter(db, globex_tenant):
    """A ProjectCharter belonging to Globex Inc."""
    return ProjectCharter.objects.create(
        tenant=globex_tenant,
        title='Globex ERP Charter',
        status='draft',
    )


@pytest.fixture
def globex_stakeholder(db, globex_tenant):
    """A Stakeholder belonging to Globex Inc."""
    return Stakeholder.objects.create(
        tenant=globex_tenant,
        name='Bob Jones',
        organization='Globex Inc',
    )


@pytest.fixture
def globex_kickoff(db, globex_tenant):
    """A KickoffTask belonging to Globex Inc."""
    return KickoffTask.objects.create(
        tenant=globex_tenant,
        title='Globex kickoff room',
        category='team',
        status='pending',
    )
