"""Tests for auth, permission, and multi-tenant isolation in the initiation app."""

import pytest
from django.urls import reverse

from apps.initiation.models import (
    BusinessCase,
    KickoffTask,
    ProjectCharter,
    ProjectRequest,
    Stakeholder,
)


# ---------------------------------------------------------------------------
# Anonymous user redirects
# ---------------------------------------------------------------------------

PROTECTED_URLS = [
    ('initiation:request_list', []),
    ('initiation:request_create', []),
    ('initiation:businesscase_list', []),
    ('initiation:businesscase_create', []),
    ('initiation:charter_list', []),
    ('initiation:charter_create', []),
    ('initiation:stakeholder_list', []),
    ('initiation:stakeholder_create', []),
    ('initiation:kickoff_list', []),
    ('initiation:kickoff_create', []),
]


@pytest.mark.parametrize('url_name,args', PROTECTED_URLS)
@pytest.mark.django_db
def test_anonymous_redirected_to_login(anon_client, url_name, args):
    url = reverse(url_name, args=args)
    r = anon_client.get(url)
    assert r.status_code in (301, 302), f"Expected redirect for {url_name}, got {r.status_code}"
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_request_detail_redirects(anon_client, acme_request):
    url = reverse('initiation:request_detail', args=[acme_request.pk])
    r = anon_client.get(url)
    assert r.status_code in (301, 302)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_charter_detail_redirects(anon_client, acme_charter):
    url = reverse('initiation:charter_detail', args=[acme_charter.pk])
    r = anon_client.get(url)
    assert r.status_code in (301, 302)
    assert 'login' in r['Location']


@pytest.mark.django_db
def test_anonymous_request_delete_redirects(anon_client, acme_request):
    url = reverse('initiation:request_delete', args=[acme_request.pk])
    r = anon_client.post(url)
    assert r.status_code in (301, 302)
    assert 'login' in r['Location']
    # Object must not be deleted
    assert ProjectRequest.objects.filter(pk=acme_request.pk).exists()


# ---------------------------------------------------------------------------
# Multi-tenant isolation: ProjectRequest
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRequestIsolation:
    def test_acme_cannot_view_globex_request(self, acme_client, globex_request):
        url = reverse('initiation:request_detail', args=[globex_request.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_request(self, acme_client, globex_request):
        url = reverse('initiation:request_edit', args=[globex_request.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_request(self, acme_client, globex_request):
        url = reverse('initiation:request_delete', args=[globex_request.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert ProjectRequest.objects.filter(pk=globex_request.pk).exists()

    def test_request_list_excludes_globex_rows(self, acme_client, acme_request, globex_request):
        url = reverse('initiation:request_list')
        r = acme_client.get(url)
        pks = [obj.pk for obj in r.context['requests']]
        assert acme_request.pk in pks
        assert globex_request.pk not in pks

    def test_globex_cannot_view_acme_request(self, globex_client, acme_request):
        url = reverse('initiation:request_detail', args=[acme_request.pk])
        r = globex_client.get(url)
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Multi-tenant isolation: BusinessCase
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestBusinessCaseIsolation:
    def test_acme_cannot_view_globex_bc(self, acme_client, globex_business_case):
        url = reverse('initiation:businesscase_detail', args=[globex_business_case.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_bc(self, acme_client, globex_business_case):
        url = reverse('initiation:businesscase_edit', args=[globex_business_case.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_bc(self, acme_client, globex_business_case):
        url = reverse('initiation:businesscase_delete', args=[globex_business_case.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert BusinessCase.objects.filter(pk=globex_business_case.pk).exists()

    def test_bc_list_excludes_globex_rows(self, acme_client, acme_business_case, globex_business_case):
        url = reverse('initiation:businesscase_list')
        r = acme_client.get(url)
        pks = [obj.pk for obj in r.context['business_cases']]
        assert acme_business_case.pk in pks
        assert globex_business_case.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: ProjectCharter
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCharterIsolation:
    def test_acme_cannot_view_globex_charter(self, acme_client, globex_charter):
        url = reverse('initiation:charter_detail', args=[globex_charter.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_charter(self, acme_client, globex_charter):
        url = reverse('initiation:charter_edit', args=[globex_charter.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_charter(self, acme_client, globex_charter):
        url = reverse('initiation:charter_delete', args=[globex_charter.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert ProjectCharter.objects.filter(pk=globex_charter.pk).exists()

    def test_charter_list_excludes_globex_rows(self, acme_client, acme_charter, globex_charter):
        url = reverse('initiation:charter_list')
        r = acme_client.get(url)
        pks = [obj.pk for obj in r.context['charters']]
        assert acme_charter.pk in pks
        assert globex_charter.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: Stakeholder
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStakeholderIsolation:
    def test_acme_cannot_view_globex_stakeholder(self, acme_client, globex_stakeholder):
        url = reverse('initiation:stakeholder_detail', args=[globex_stakeholder.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_stakeholder(self, acme_client, globex_stakeholder):
        url = reverse('initiation:stakeholder_edit', args=[globex_stakeholder.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_stakeholder(self, acme_client, globex_stakeholder):
        url = reverse('initiation:stakeholder_delete', args=[globex_stakeholder.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert Stakeholder.objects.filter(pk=globex_stakeholder.pk).exists()

    def test_stakeholder_list_excludes_globex_rows(
        self, acme_client, acme_stakeholder, globex_stakeholder
    ):
        url = reverse('initiation:stakeholder_list')
        r = acme_client.get(url)
        pks = [obj.pk for obj in r.context['stakeholders']]
        assert acme_stakeholder.pk in pks
        assert globex_stakeholder.pk not in pks


# ---------------------------------------------------------------------------
# Multi-tenant isolation: KickoffTask
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestKickoffTaskIsolation:
    def test_acme_cannot_view_globex_kickoff(self, acme_client, globex_kickoff):
        url = reverse('initiation:kickoff_detail', args=[globex_kickoff.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_edit_globex_kickoff(self, acme_client, globex_kickoff):
        url = reverse('initiation:kickoff_edit', args=[globex_kickoff.pk])
        r = acme_client.get(url)
        assert r.status_code == 404

    def test_acme_cannot_delete_globex_kickoff(self, acme_client, globex_kickoff):
        url = reverse('initiation:kickoff_delete', args=[globex_kickoff.pk])
        r = acme_client.post(url)
        assert r.status_code == 404
        assert KickoffTask.objects.filter(pk=globex_kickoff.pk).exists()

    def test_kickoff_list_excludes_globex_rows(
        self, acme_client, acme_kickoff, globex_kickoff
    ):
        url = reverse('initiation:kickoff_list')
        r = acme_client.get(url)
        pks = [obj.pk for obj in r.context['kickoff_tasks']]
        assert acme_kickoff.pk in pks
        assert globex_kickoff.pk not in pks


# ---------------------------------------------------------------------------
# CSRF enforcement
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCSRFEnforcement:
    def test_csrf_required_on_request_create(self, acme_admin):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('initiation:request_create')
        r = c.post(url, {
            'title': 'Injected',
            'estimated_budget': '0',
            'priority': 'medium',
            'status': 'draft',
        })
        assert r.status_code == 403

    def test_csrf_required_on_request_delete(self, acme_admin, acme_request):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('initiation:request_delete', args=[acme_request.pk])
        r = c.post(url)
        assert r.status_code == 403
        assert ProjectRequest.objects.filter(pk=acme_request.pk).exists()

    def test_csrf_required_on_charter_create(self, acme_admin):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('initiation:charter_create')
        r = c.post(url, {
            'title': 'CSRF Injected Charter',
            'budget': '0',
            'status': 'draft',
        })
        assert r.status_code == 403

    def test_csrf_required_on_stakeholder_delete(self, acme_admin, acme_stakeholder):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.force_login(acme_admin)
        url = reverse('initiation:stakeholder_delete', args=[acme_stakeholder.pk])
        r = c.post(url)
        assert r.status_code == 403
        assert Stakeholder.objects.filter(pk=acme_stakeholder.pk).exists()


# ---------------------------------------------------------------------------
# Belt-and-suspenders: Globex list excludes Acme rows
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_globex_request_list_excludes_acme(globex_client, acme_request, globex_request):
    url = reverse('initiation:request_list')
    r = globex_client.get(url)
    pks = [obj.pk for obj in r.context['requests']]
    assert globex_request.pk in pks
    assert acme_request.pk not in pks


@pytest.mark.django_db
def test_globex_charter_list_excludes_acme(globex_client, acme_charter, globex_charter):
    url = reverse('initiation:charter_list')
    r = globex_client.get(url)
    pks = [obj.pk for obj in r.context['charters']]
    assert globex_charter.pk in pks
    assert acme_charter.pk not in pks
