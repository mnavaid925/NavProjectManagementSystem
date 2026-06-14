"""Tests for auth, permission, and multi-tenant isolation in the planning app."""
import datetime

import pytest
from django.urls import reverse

from apps.planning.models import (
    Milestone,
    ScheduleBaseline,
    ScheduleTask,
    TaskDependency,
    WorkPackage,
)


# ---------------------------------------------------------------------------
# Anonymous user redirects
# ---------------------------------------------------------------------------

PROTECTED_URLS = [
    ('planning:workpackage_list', []),
    ('planning:workpackage_create', []),
    ('planning:task_list', []),
    ('planning:task_create', []),
    ('planning:dependency_list', []),
    ('planning:dependency_create', []),
    ('planning:milestone_list', []),
    ('planning:milestone_create', []),
    ('planning:baseline_list', []),
    ('planning:baseline_create', []),
]


@pytest.mark.parametrize('url_name,args', PROTECTED_URLS)
@pytest.mark.django_db
def test_anonymous_redirected_to_login(anon_client, url_name, args):
    url = reverse(url_name, args=args)
    r = anon_client.get(url)
    assert r.status_code in (302, 301), (
        f"Expected redirect for {url_name}, got {r.status_code}"
    )
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_workpackage_detail_redirects(anon_client, acme_work_package):
    url = reverse('planning:workpackage_detail', args=[acme_work_package.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_task_detail_redirects(anon_client, acme_task):
    url = reverse('planning:task_detail', args=[acme_task.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_milestone_detail_redirects(anon_client, acme_milestone):
    url = reverse('planning:milestone_detail', args=[acme_milestone.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_baseline_detail_redirects(anon_client, acme_baseline):
    url = reverse('planning:baseline_detail', args=[acme_baseline.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_dependency_detail_redirects(anon_client, acme_dependency):
    url = reverse('planning:dependency_detail', args=[acme_dependency.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


# ---------------------------------------------------------------------------
# Multi-tenant isolation: WorkPackage
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestWorkPackageIsolation:
    def test_acme_cannot_see_globex_workpackage_detail(
        self, acme_client, globex_work_package
    ):
        url = reverse('planning:workpackage_detail', args=[globex_work_package.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_workpackage(
        self, acme_client, globex_work_package
    ):
        url = reverse('planning:workpackage_edit', args=[globex_work_package.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_workpackage(
        self, acme_client, globex_work_package
    ):
        url = reverse('planning:workpackage_delete', args=[globex_work_package.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert WorkPackage.objects.filter(pk=globex_work_package.pk).exists()

    def test_workpackage_list_excludes_globex_rows(
        self, acme_client, acme_work_package, globex_work_package
    ):
        url = reverse('planning:workpackage_list')
        r = acme_client.get(url)
        pks = [wp.pk for wp in r.context['work_packages']]
        assert acme_work_package.pk in pks
        assert globex_work_package.pk not in pks

    def test_globex_cannot_see_acme_workpackage(
        self, globex_client, acme_work_package
    ):
        url = reverse('planning:workpackage_detail', args=[acme_work_package.pk])
        r = globex_client.get(url)
        assert r.status_code == 404

    def test_globex_list_excludes_acme_workpackages(
        self, globex_client, acme_work_package, globex_work_package
    ):
        url = reverse('planning:workpackage_list')
        r = globex_client.get(url)
        pks = [wp.pk for wp in r.context['work_packages']]
        assert globex_work_package.pk in pks
        assert acme_work_package.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: ScheduleTask
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestScheduleTaskIsolation:
    def test_acme_cannot_see_globex_task_detail(self, acme_client, globex_task):
        url = reverse('planning:task_detail', args=[globex_task.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_task(self, acme_client, globex_task):
        url = reverse('planning:task_edit', args=[globex_task.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_task(self, acme_client, globex_task):
        url = reverse('planning:task_delete', args=[globex_task.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert ScheduleTask.objects.filter(pk=globex_task.pk).exists()

    def test_task_list_excludes_globex_rows(
        self, acme_client, acme_task, globex_task
    ):
        url = reverse('planning:task_list')
        r = acme_client.get(url)
        pks = [t.pk for t in r.context['tasks']]
        assert acme_task.pk in pks
        assert globex_task.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: TaskDependency
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTaskDependencyIsolation:
    def test_acme_cannot_see_globex_dependency_detail(
        self, acme_client, globex_dependency
    ):
        url = reverse('planning:dependency_detail', args=[globex_dependency.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_dependency(
        self, acme_client, globex_dependency
    ):
        url = reverse('planning:dependency_edit', args=[globex_dependency.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_dependency(
        self, acme_client, globex_dependency
    ):
        url = reverse('planning:dependency_delete', args=[globex_dependency.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert TaskDependency.objects.filter(pk=globex_dependency.pk).exists()

    def test_dependency_list_excludes_globex_rows(
        self, acme_client, acme_dependency, globex_dependency
    ):
        url = reverse('planning:dependency_list')
        r = acme_client.get(url)
        pks = [d.pk for d in r.context['dependencies']]
        assert acme_dependency.pk in pks
        assert globex_dependency.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: Milestone
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMilestoneIsolation:
    def test_acme_cannot_see_globex_milestone_detail(
        self, acme_client, globex_milestone
    ):
        url = reverse('planning:milestone_detail', args=[globex_milestone.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_milestone(
        self, acme_client, globex_milestone
    ):
        url = reverse('planning:milestone_edit', args=[globex_milestone.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_milestone(
        self, acme_client, globex_milestone
    ):
        url = reverse('planning:milestone_delete', args=[globex_milestone.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert Milestone.objects.filter(pk=globex_milestone.pk).exists()

    def test_milestone_list_excludes_globex_rows(
        self, acme_client, acme_milestone, globex_milestone
    ):
        url = reverse('planning:milestone_list')
        r = acme_client.get(url)
        pks = [ms.pk for ms in r.context['milestones']]
        assert acme_milestone.pk in pks
        assert globex_milestone.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: ScheduleBaseline
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestScheduleBaselineIsolation:
    def test_acme_cannot_see_globex_baseline_detail(
        self, acme_client, globex_baseline
    ):
        url = reverse('planning:baseline_detail', args=[globex_baseline.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_baseline(
        self, acme_client, globex_baseline
    ):
        url = reverse('planning:baseline_edit', args=[globex_baseline.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_baseline(
        self, acme_client, globex_baseline
    ):
        url = reverse('planning:baseline_delete', args=[globex_baseline.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert ScheduleBaseline.objects.filter(pk=globex_baseline.pk).exists()

    def test_baseline_list_excludes_globex_rows(
        self, acme_client, acme_baseline, globex_baseline
    ):
        url = reverse('planning:baseline_list')
        r = acme_client.get(url)
        pks = [b.pk for b in r.context['baselines']]
        assert acme_baseline.pk in pks
        assert globex_baseline.pk not in pks


# ---------------------------------------------------------------------------
# CSRF enforcement
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCSRFEnforcement:
    def test_csrf_required_on_workpackage_create(self, acme_admin):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('planning:workpackage_create')
        r = c.post(url, {
            'code': '1.0',
            'name': 'CSRF WP',
            'project': '',
            'parent': '',
            'description': '',
            'level': '1',
            'estimated_effort_hours': '0',
            'owner': '',
            'status': 'not_started',
        })
        assert r.status_code == 403

    def test_csrf_required_on_task_create(self, acme_admin):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('planning:task_create')
        r = c.post(url, {
            'name': 'CSRF Task',
            'duration_days': '1',
            'effort_hours': '0',
            'estimate_method': 'bottom_up',
            'percent_complete': '0',
            'status': 'not_started',
        })
        assert r.status_code == 403

    def test_csrf_required_on_workpackage_delete(self, acme_admin, acme_work_package):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('planning:workpackage_delete', args=[acme_work_package.pk])
        r = c.post(url)
        assert r.status_code == 403
        # Object must still exist
        assert WorkPackage.objects.filter(pk=acme_work_package.pk).exists()

    def test_csrf_required_on_milestone_delete(self, acme_admin, acme_milestone):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('planning:milestone_delete', args=[acme_milestone.pk])
        r = c.post(url)
        assert r.status_code == 403
        assert Milestone.objects.filter(pk=acme_milestone.pk).exists()

    def test_csrf_required_on_baseline_create(self, acme_admin):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('planning:baseline_create')
        r = c.post(url, {
            'name': 'CSRF BL',
            'version': '',
            'status': 'draft',
            'is_current': False,
            'notes': '',
        })
        assert r.status_code == 403


# ---------------------------------------------------------------------------
# Auth: non-admin users still have access (no admin-only gate in planning)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestNonAdminUserAccess:
    """Planning views have no is_tenant_admin gate; any authenticated user can CRUD."""

    def test_regular_user_can_list_workpackages(self, acme_user_client):
        url = reverse('planning:workpackage_list')
        r = acme_user_client.get(url)
        assert r.status_code == 200

    def test_regular_user_can_list_tasks(self, acme_user_client):
        url = reverse('planning:task_list')
        r = acme_user_client.get(url)
        assert r.status_code == 200

    def test_regular_user_can_list_milestones(self, acme_user_client):
        url = reverse('planning:milestone_list')
        r = acme_user_client.get(url)
        assert r.status_code == 200

    def test_regular_user_can_list_baselines(self, acme_user_client):
        url = reverse('planning:baseline_list')
        r = acme_user_client.get(url)
        assert r.status_code == 200

    def test_regular_user_can_create_workpackage(self, acme_user_client, acme_tenant):
        url = reverse('planning:workpackage_create')
        r = acme_user_client.post(url, {
            'code': '9.9',
            'name': 'User WP',
            'project': '',
            'parent': '',
            'description': '',
            'level': '1',
            'estimated_effort_hours': '0',
            'owner': '',
            'status': 'not_started',
        })
        assert r.status_code == 302
        assert WorkPackage.objects.filter(tenant=acme_tenant, name='User WP').exists()
