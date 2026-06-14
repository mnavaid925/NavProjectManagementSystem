"""Tests for auth, permission, CSRF, and multi-tenant isolation in the resources app."""
import datetime
from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from apps.resources.models import (
    Allocation,
    DemandForecast,
    Resource,
    Skill,
    TeamAssignment,
    TimeEntry,
)


# ---------------------------------------------------------------------------
# Anonymous user redirect tests
# ---------------------------------------------------------------------------
PROTECTED_URLS = [
    ('resources:skill_list', []),
    ('resources:skill_create', []),
    ('resources:resource_list', []),
    ('resources:resource_create', []),
    ('resources:allocation_list', []),
    ('resources:allocation_create', []),
    ('resources:assignment_list', []),
    ('resources:assignment_create', []),
    ('resources:forecast_list', []),
    ('resources:forecast_create', []),
    ('resources:timeentry_list', []),
    ('resources:timeentry_create', []),
]


@pytest.mark.parametrize('url_name,args', PROTECTED_URLS)
@pytest.mark.django_db
def test_anonymous_redirected_to_login(anon_client, url_name, args):
    url = reverse(url_name, args=args)
    r = anon_client.get(url)
    assert r.status_code in (302, 301), (
        f"Expected redirect for {url_name}, got {r.status_code}"
    )
    location = r['Location']
    assert '/login/' in location or 'login' in location


@pytest.mark.django_db
def test_anonymous_skill_detail_redirects(anon_client, acme_skill):
    url = reverse('resources:skill_detail', args=[acme_skill.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_resource_detail_redirects(anon_client, acme_resource):
    url = reverse('resources:resource_detail', args=[acme_resource.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_timeentry_detail_redirects(anon_client, acme_time_entry):
    url = reverse('resources:timeentry_detail', args=[acme_time_entry.pk])
    r = anon_client.get(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_skill_delete_post_redirects(anon_client, acme_skill):
    url = reverse('resources:skill_delete', args=[acme_skill.pk])
    r = anon_client.post(url)
    assert r.status_code in (302, 301)
    assert 'login' in r['Location']
    # Object must still exist
    assert Skill.objects.filter(pk=acme_skill.pk).exists()


@pytest.mark.django_db
def test_anonymous_resource_delete_post_redirects(anon_client, acme_resource):
    url = reverse('resources:resource_delete', args=[acme_resource.pk])
    r = anon_client.post(url)
    assert r.status_code in (302, 301)
    assert Resource.objects.filter(pk=acme_resource.pk).exists()


@pytest.mark.django_db
def test_anonymous_timeentry_delete_post_redirects(anon_client, acme_time_entry):
    url = reverse('resources:timeentry_delete', args=[acme_time_entry.pk])
    r = anon_client.post(url)
    assert r.status_code in (302, 301)
    assert TimeEntry.objects.filter(pk=acme_time_entry.pk).exists()


# ---------------------------------------------------------------------------
# Multi-tenant isolation: Skills
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSkillIsolation:
    def test_acme_cannot_view_globex_skill(self, acme_client, globex_skill):
        url = reverse('resources:skill_detail', args=[globex_skill.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_skill(self, acme_client, globex_skill):
        url = reverse('resources:skill_edit', args=[globex_skill.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_skill(self, acme_client, globex_skill):
        url = reverse('resources:skill_delete', args=[globex_skill.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert Skill.objects.filter(pk=globex_skill.pk).exists()

    def test_skill_list_excludes_globex_skills(self, acme_client, acme_skill, globex_skill):
        url = reverse('resources:skill_list')
        r = acme_client.get(url)
        pks = [s.pk for s in r.context['skills']]
        assert acme_skill.pk in pks
        assert globex_skill.pk not in pks

    def test_globex_cannot_view_acme_skill(self, globex_client, acme_skill):
        url = reverse('resources:skill_detail', args=[acme_skill.pk])
        r = globex_client.get(url)
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Multi-tenant isolation: Resources
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestResourceIsolation:
    def test_acme_cannot_view_globex_resource(self, acme_client, globex_resource):
        url = reverse('resources:resource_detail', args=[globex_resource.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_resource(self, acme_client, globex_resource):
        url = reverse('resources:resource_edit', args=[globex_resource.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_resource(self, acme_client, globex_resource):
        url = reverse('resources:resource_delete', args=[globex_resource.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert Resource.objects.filter(pk=globex_resource.pk).exists()

    def test_resource_list_excludes_globex(self, acme_client, acme_resource, globex_resource):
        url = reverse('resources:resource_list')
        r = acme_client.get(url)
        pks = [res.pk for res in r.context['resources']]
        assert acme_resource.pk in pks
        assert globex_resource.pk not in pks

    def test_globex_cannot_view_acme_resource(self, globex_client, acme_resource):
        url = reverse('resources:resource_detail', args=[acme_resource.pk])
        r = globex_client.get(url)
        assert r.status_code == 404

    def test_globex_resource_list_excludes_acme(self, globex_client, acme_resource, globex_resource):
        url = reverse('resources:resource_list')
        r = globex_client.get(url)
        pks = [res.pk for res in r.context['resources']]
        assert globex_resource.pk in pks
        assert acme_resource.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: Allocations
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAllocationIsolation:
    def test_acme_cannot_view_globex_allocation(self, acme_client, globex_allocation):
        url = reverse('resources:allocation_detail', args=[globex_allocation.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_allocation(self, acme_client, globex_allocation):
        url = reverse('resources:allocation_edit', args=[globex_allocation.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_allocation(self, acme_client, globex_allocation):
        url = reverse('resources:allocation_delete', args=[globex_allocation.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert Allocation.objects.filter(pk=globex_allocation.pk).exists()

    def test_allocation_list_excludes_globex(self, acme_client, acme_allocation, globex_allocation):
        url = reverse('resources:allocation_list')
        r = acme_client.get(url)
        pks = [a.pk for a in r.context['allocations']]
        assert acme_allocation.pk in pks
        assert globex_allocation.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: Team Assignments
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAssignmentIsolation:
    def test_acme_cannot_view_globex_assignment(self, acme_client, globex_assignment):
        url = reverse('resources:assignment_detail', args=[globex_assignment.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_assignment(self, acme_client, globex_assignment):
        url = reverse('resources:assignment_edit', args=[globex_assignment.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_assignment(self, acme_client, globex_assignment):
        url = reverse('resources:assignment_delete', args=[globex_assignment.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert TeamAssignment.objects.filter(pk=globex_assignment.pk).exists()

    def test_assignment_list_excludes_globex(self, acme_client, acme_assignment, globex_assignment):
        url = reverse('resources:assignment_list')
        r = acme_client.get(url)
        pks = [a.pk for a in r.context['assignments']]
        assert acme_assignment.pk in pks
        assert globex_assignment.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: Demand Forecasts
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestForecastIsolation:
    def test_acme_cannot_view_globex_forecast(self, acme_client, globex_forecast):
        url = reverse('resources:forecast_detail', args=[globex_forecast.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_forecast(self, acme_client, globex_forecast):
        url = reverse('resources:forecast_edit', args=[globex_forecast.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_forecast(self, acme_client, globex_forecast):
        url = reverse('resources:forecast_delete', args=[globex_forecast.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert DemandForecast.objects.filter(pk=globex_forecast.pk).exists()

    def test_forecast_list_excludes_globex(self, acme_client, acme_forecast, globex_forecast):
        url = reverse('resources:forecast_list')
        r = acme_client.get(url)
        pks = [f.pk for f in r.context['forecasts']]
        assert acme_forecast.pk in pks
        assert globex_forecast.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: Time Entries
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTimeEntryIsolation:
    def test_acme_cannot_view_globex_timeentry(self, acme_client, globex_time_entry):
        url = reverse('resources:timeentry_detail', args=[globex_time_entry.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_timeentry(self, acme_client, globex_time_entry):
        url = reverse('resources:timeentry_edit', args=[globex_time_entry.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_timeentry(self, acme_client, globex_time_entry):
        url = reverse('resources:timeentry_delete', args=[globex_time_entry.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert TimeEntry.objects.filter(pk=globex_time_entry.pk).exists()

    def test_timeentry_list_excludes_globex(self, acme_client, acme_time_entry, globex_time_entry):
        url = reverse('resources:timeentry_list')
        r = acme_client.get(url)
        pks = [te.pk for te in r.context['time_entries']]
        assert acme_time_entry.pk in pks
        assert globex_time_entry.pk not in pks

    def test_globex_cannot_view_acme_timeentry(self, globex_client, acme_time_entry):
        url = reverse('resources:timeentry_detail', args=[acme_time_entry.pk])
        r = globex_client.get(url)
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# CSRF enforcement
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestCSRFEnforcement:
    def test_csrf_required_on_skill_create(self, acme_admin):
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('resources:skill_create')
        r = c.post(url, {'name': 'Injected', 'category': 'technical', 'description': ''})
        assert r.status_code == 403

    def test_csrf_required_on_resource_create(self, acme_admin):
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('resources:resource_create')
        r = c.post(url, {
            'name': 'Injected Resource',
            'resource_type': 'employee',
            'capacity_hours_per_week': 40,
            'cost_rate': '0',
            'is_active': True,
        })
        assert r.status_code == 403

    def test_csrf_required_on_timeentry_create(self, acme_admin, acme_resource):
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('resources:timeentry_create')
        r = c.post(url, {
            'resource': acme_resource.pk,
            'work_date': '2026-07-01',
            'hours': '8',
            'is_billable': True,
            'status': 'draft',
        })
        assert r.status_code == 403

    def test_csrf_required_on_skill_delete(self, acme_admin, acme_skill):
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('resources:skill_delete', args=[acme_skill.pk])
        r = c.post(url)
        assert r.status_code == 403
        assert Skill.objects.filter(pk=acme_skill.pk).exists()

    def test_csrf_required_on_resource_delete(self, acme_admin, acme_resource):
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('resources:resource_delete', args=[acme_resource.pk])
        r = c.post(url)
        assert r.status_code == 403
        assert Resource.objects.filter(pk=acme_resource.pk).exists()

    def test_csrf_required_on_allocation_delete(self, acme_admin, acme_allocation):
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('resources:allocation_delete', args=[acme_allocation.pk])
        r = c.post(url)
        assert r.status_code == 403
        assert Allocation.objects.filter(pk=acme_allocation.pk).exists()

    def test_csrf_required_on_timeentry_delete(self, acme_admin, acme_time_entry):
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('resources:timeentry_delete', args=[acme_time_entry.pk])
        r = c.post(url)
        assert r.status_code == 403
        assert TimeEntry.objects.filter(pk=acme_time_entry.pk).exists()


# ---------------------------------------------------------------------------
# Resource with user=None — list and detail no 500
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestResourceNullUser:
    def test_null_user_resource_appears_in_list(self, acme_client, acme_resource_no_user):
        url = reverse('resources:resource_list')
        r = acme_client.get(url)
        assert r.status_code == 200
        names = [res.name for res in r.context['resources']]
        assert 'Bob Contractor' in names

    def test_null_user_resource_detail_no_500(self, acme_client, acme_resource_no_user):
        url = reverse('resources:resource_detail', args=[acme_resource_no_user.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        # Page should render the resource name without crashing
        assert b'Bob Contractor' in r.content

    def test_null_user_resource_edit_no_500(self, acme_client, acme_resource_no_user):
        url = reverse('resources:resource_edit', args=[acme_resource_no_user.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
