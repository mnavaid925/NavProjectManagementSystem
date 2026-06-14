"""Shared pytest fixtures for the planning app test suite."""
import datetime

import pytest
from django.test import Client

from apps.accounts.models import User
from apps.core.models import Tenant
from apps.planning.models import (
    Milestone,
    ScheduleBaseline,
    ScheduleTask,
    TaskDependency,
    WorkPackage,
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
    """Secondary test tenant for isolation checks (Globex Inc)."""
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
def acme_client(acme_admin):
    """Django test Client pre-logged-in as the Acme tenant admin."""
    c = Client()
    c.force_login(acme_admin)
    return c


@pytest.fixture
def acme_user_client(acme_user):
    """Django test Client logged in as a non-admin Acme user."""
    c = Client()
    c.force_login(acme_user)
    return c


@pytest.fixture
def globex_client(globex_admin):
    """Django test Client pre-logged-in as the Globex tenant admin."""
    c = Client()
    c.force_login(globex_admin)
    return c


@pytest.fixture
def anon_client():
    """Unauthenticated Django test Client."""
    return Client()


# ---------------------------------------------------------------------------
# Planning model fixtures (Acme)
# ---------------------------------------------------------------------------

@pytest.fixture
def acme_work_package(db, acme_tenant):
    """A WorkPackage belonging to Acme."""
    return WorkPackage.objects.create(
        tenant=acme_tenant,
        code='1.1',
        name='Acme WP Alpha',
        level=1,
    )


@pytest.fixture
def globex_work_package(db, globex_tenant):
    """A WorkPackage belonging to Globex (used in isolation tests)."""
    return WorkPackage.objects.create(
        tenant=globex_tenant,
        code='2.1',
        name='Globex WP Beta',
        level=1,
    )


@pytest.fixture
def acme_task(db, acme_tenant):
    """A ScheduleTask belonging to Acme."""
    return ScheduleTask.objects.create(
        tenant=acme_tenant,
        name='Acme Task Alpha',
        start_date=datetime.date(2025, 1, 1),
        end_date=datetime.date(2025, 1, 10),
        duration_days=10,
    )


@pytest.fixture
def acme_task2(db, acme_tenant):
    """A second ScheduleTask belonging to Acme (for dependency tests)."""
    return ScheduleTask.objects.create(
        tenant=acme_tenant,
        name='Acme Task Beta',
        start_date=datetime.date(2025, 1, 11),
        end_date=datetime.date(2025, 1, 20),
        duration_days=10,
    )


@pytest.fixture
def globex_task(db, globex_tenant):
    """A ScheduleTask belonging to Globex (used in isolation tests)."""
    return ScheduleTask.objects.create(
        tenant=globex_tenant,
        name='Globex Task Beta',
        duration_days=5,
    )


@pytest.fixture
def acme_dependency(db, acme_tenant, acme_task, acme_task2):
    """A TaskDependency (FS) between two Acme tasks."""
    return TaskDependency.objects.create(
        tenant=acme_tenant,
        predecessor=acme_task,
        successor=acme_task2,
        dependency_type='FS',
        lag_days=0,
    )


@pytest.fixture
def globex_dependency(db, globex_tenant, globex_task):
    """A TaskDependency belonging to Globex (used in isolation tests)."""
    globex_task2 = ScheduleTask.objects.create(
        tenant=globex_tenant,
        name='Globex Task Gamma',
        duration_days=3,
    )
    return TaskDependency.objects.create(
        tenant=globex_tenant,
        predecessor=globex_task,
        successor=globex_task2,
        dependency_type='SS',
    )


@pytest.fixture
def acme_milestone(db, acme_tenant):
    """A Milestone belonging to Acme."""
    return Milestone.objects.create(
        tenant=acme_tenant,
        name='Acme Milestone Alpha',
        due_date=datetime.date(2025, 6, 30),
        milestone_type='milestone',
    )


@pytest.fixture
def globex_milestone(db, globex_tenant):
    """A Milestone belonging to Globex (used in isolation tests)."""
    return Milestone.objects.create(
        tenant=globex_tenant,
        name='Globex Milestone Beta',
        due_date=datetime.date(2025, 7, 31),
        milestone_type='phase_gate',
    )


@pytest.fixture
def acme_baseline(db, acme_tenant):
    """A ScheduleBaseline belonging to Acme."""
    return ScheduleBaseline.objects.create(
        tenant=acme_tenant,
        name='Acme Baseline v1',
        version='v1.0',
        baseline_date=datetime.date(2025, 1, 1),
        status='draft',
    )


@pytest.fixture
def globex_baseline(db, globex_tenant):
    """A ScheduleBaseline belonging to Globex (used in isolation tests)."""
    return ScheduleBaseline.objects.create(
        tenant=globex_tenant,
        name='Globex Baseline v1',
        version='v1.0',
        baseline_date=datetime.date(2025, 2, 1),
        status='approved',
    )
