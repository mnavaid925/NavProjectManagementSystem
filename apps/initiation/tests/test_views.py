"""Tests for initiation app views: CRUD, context keys, templates, pagination."""
import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.initiation.models import (
    BusinessCase,
    KickoffTask,
    ProjectCharter,
    ProjectRequest,
    Stakeholder,
)


# ===========================================================================
# ProjectRequest views
# ===========================================================================

@pytest.mark.django_db
class TestRequestListView:
    def test_200_for_logged_in(self, acme_client, acme_request):
        url = reverse('initiation:request_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('initiation:request_list')
        r = acme_client.get(url)
        assert 'initiation/request_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client, acme_request):
        url = reverse('initiation:request_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'requests' in r.context
        assert 'status_choices' in r.context
        assert 'priority_choices' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_request, db, acme_tenant):
        other = ProjectRequest.objects.create(
            tenant=acme_tenant, title='Unrelated Task', priority='low',
        )
        url = reverse('initiation:request_list')
        r = acme_client.get(url, {'q': 'Portal'})
        pks = [obj.pk for obj in r.context['requests']]
        assert acme_request.pk in pks
        assert other.pk not in pks

    def test_status_filter(self, acme_client, db, acme_tenant, acme_request):
        submitted = ProjectRequest.objects.create(
            tenant=acme_tenant, title='Submitted', status='submitted',
        )
        url = reverse('initiation:request_list')
        r = acme_client.get(url, {'status': 'submitted'})
        pks = [obj.pk for obj in r.context['requests']]
        assert submitted.pk in pks
        assert acme_request.pk not in pks  # acme_request is 'draft'

    def test_priority_filter(self, acme_client, db, acme_tenant, acme_request):
        low = ProjectRequest.objects.create(
            tenant=acme_tenant, title='Low Priority', priority='low',
        )
        url = reverse('initiation:request_list')
        r = acme_client.get(url, {'priority': 'low'})
        pks = [obj.pk for obj in r.context['requests']]
        assert low.pk in pks
        assert acme_request.pk not in pks  # acme_request is 'high'

    def test_pagination_max_10(self, acme_client, db, acme_tenant):
        for i in range(12):
            ProjectRequest.objects.create(tenant=acme_tenant, title=f'Request {i:02d}')
        url = reverse('initiation:request_list')
        r = acme_client.get(url)
        assert len(r.context['requests']) <= 10


@pytest.mark.django_db
class TestRequestDetailView:
    def test_200_for_owner(self, acme_client, acme_request):
        url = reverse('initiation:request_detail', args=[acme_request.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_var_is_obj(self, acme_client, acme_request):
        url = reverse('initiation:request_detail', args=[acme_request.pk])
        r = acme_client.get(url)
        assert 'obj' in r.context
        assert r.context['obj'].pk == acme_request.pk

    def test_detail_html_contains_number(self, acme_client, acme_request):
        """Detail page must render the object's auto-number to catch silent blank."""
        url = reverse('initiation:request_detail', args=[acme_request.pk])
        r = acme_client.get(url)
        assert acme_request.number.encode() in r.content


@pytest.mark.django_db
class TestRequestCreateView:
    def test_get_form(self, acme_client):
        url = reverse('initiation:request_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('initiation:request_create')
        r = acme_client.post(url, {
            'title': 'New Request',
            'department': 'HR',
            'description': '',
            'expected_benefit': '',
            'estimated_budget': '5000',
            'priority': 'high',
            'status': 'draft',
            'target_start_date': '',
            'requested_by': '',
            'project': '',
        })
        assert r.status_code == 302
        obj = ProjectRequest.objects.filter(tenant=acme_tenant, title='New Request').first()
        assert obj is not None
        assert obj.tenant == acme_tenant

    def test_post_does_not_save_without_title(self, acme_client, acme_tenant):
        count_before = ProjectRequest.objects.filter(tenant=acme_tenant).count()
        url = reverse('initiation:request_create')
        r = acme_client.post(url, {
            'title': '',
            'estimated_budget': '0',
            'priority': 'medium',
            'status': 'draft',
        })
        assert r.status_code == 200  # re-renders form
        assert ProjectRequest.objects.filter(tenant=acme_tenant).count() == count_before


@pytest.mark.django_db
class TestRequestEditView:
    def test_get_edit_form(self, acme_client, acme_request):
        url = reverse('initiation:request_edit', args=[acme_request.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'obj' in r.context

    def test_post_updates_request(self, acme_client, acme_request):
        url = reverse('initiation:request_edit', args=[acme_request.pk])
        r = acme_client.post(url, {
            'title': 'Updated Portal',
            'department': 'Engineering',
            'description': '',
            'expected_benefit': '',
            'estimated_budget': '10000',
            'priority': 'urgent',
            'status': 'submitted',
            'target_start_date': '',
            'requested_by': '',
            'project': '',
        })
        assert r.status_code == 302
        acme_request.refresh_from_db()
        assert acme_request.title == 'Updated Portal'
        assert acme_request.status == 'submitted'


@pytest.mark.django_db
class TestRequestDeleteView:
    def test_post_deletes(self, acme_client, acme_request):
        pk = acme_request.pk
        url = reverse('initiation:request_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not ProjectRequest.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_request):
        pk = acme_request.pk
        url = reverse('initiation:request_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert ProjectRequest.objects.filter(pk=pk).exists()


# ===========================================================================
# BusinessCase views
# ===========================================================================

@pytest.mark.django_db
class TestBusinessCaseListView:
    def test_200(self, acme_client, acme_business_case):
        url = reverse('initiation:businesscase_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('initiation:businesscase_list')
        r = acme_client.get(url)
        assert 'initiation/businesscase_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client):
        url = reverse('initiation:businesscase_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'business_cases' in r.context
        assert 'status_choices' in r.context
        assert 'recommendation_choices' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_business_case, db, acme_tenant):
        other = BusinessCase.objects.create(
            tenant=acme_tenant, title='Unrelated BC', recommendation='no_go',
        )
        url = reverse('initiation:businesscase_list')
        r = acme_client.get(url, {'q': 'Portal'})
        pks = [obj.pk for obj in r.context['business_cases']]
        assert acme_business_case.pk in pks
        assert other.pk not in pks

    def test_status_filter(self, acme_client, db, acme_tenant, acme_business_case):
        approved = BusinessCase.objects.create(
            tenant=acme_tenant, title='Approved BC', status='approved',
        )
        url = reverse('initiation:businesscase_list')
        r = acme_client.get(url, {'status': 'approved'})
        pks = [obj.pk for obj in r.context['business_cases']]
        assert approved.pk in pks
        assert acme_business_case.pk not in pks

    def test_pagination_max_10(self, acme_client, db, acme_tenant):
        for i in range(12):
            BusinessCase.objects.create(tenant=acme_tenant, title=f'BC {i:02d}')
        url = reverse('initiation:businesscase_list')
        r = acme_client.get(url)
        assert len(r.context['business_cases']) <= 10

    def test_recommendation_filter(self, acme_client, db, acme_tenant, acme_business_case):
        no_go = BusinessCase.objects.create(
            tenant=acme_tenant, title='No-Go BC', recommendation='no_go',
        )
        url = reverse('initiation:businesscase_list')
        r = acme_client.get(url, {'recommendation': 'no_go'})
        pks = [obj.pk for obj in r.context['business_cases']]
        assert no_go.pk in pks
        assert acme_business_case.pk not in pks  # acme_business_case is 'go'


@pytest.mark.django_db
class TestBusinessCaseDetailView:
    def test_200(self, acme_client, acme_business_case):
        url = reverse('initiation:businesscase_detail', args=[acme_business_case.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_var_is_businesscase(self, acme_client, acme_business_case):
        url = reverse('initiation:businesscase_detail', args=[acme_business_case.pk])
        r = acme_client.get(url)
        assert 'businesscase' in r.context
        assert r.context['businesscase'].pk == acme_business_case.pk

    def test_detail_html_contains_number(self, acme_client, acme_business_case):
        url = reverse('initiation:businesscase_detail', args=[acme_business_case.pk])
        r = acme_client.get(url)
        assert acme_business_case.number.encode() in r.content


@pytest.mark.django_db
class TestBusinessCaseCreateView:
    def test_get_form(self, acme_client):
        url = reverse('initiation:businesscase_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('initiation:businesscase_create')
        r = acme_client.post(url, {
            'title': 'Cloud Migration BC',
            'summary': 'Move to cloud',
            'problem_statement': '',
            'expected_roi': '0',
            'estimated_cost': '50000',
            'estimated_benefit': '100000',
            'payback_months': '12',
            'recommendation': 'go',
            'status': 'draft',
            'request': '',
        })
        assert r.status_code == 302
        obj = BusinessCase.objects.filter(tenant=acme_tenant, title='Cloud Migration BC').first()
        assert obj is not None
        assert obj.tenant == acme_tenant


@pytest.mark.django_db
class TestBusinessCaseEditView:
    def test_get_edit_form(self, acme_client, acme_business_case):
        url = reverse('initiation:businesscase_edit', args=[acme_business_case.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'businesscase' in r.context

    def test_post_updates(self, acme_client, acme_business_case):
        url = reverse('initiation:businesscase_edit', args=[acme_business_case.pk])
        r = acme_client.post(url, {
            'title': 'Updated BC',
            'summary': '',
            'problem_statement': '',
            'expected_roi': '10',
            'estimated_cost': '0',
            'estimated_benefit': '0',
            'payback_months': '0',
            'recommendation': 'hold',
            'status': 'in_review',
            'request': '',
        })
        assert r.status_code == 302
        acme_business_case.refresh_from_db()
        assert acme_business_case.title == 'Updated BC'
        assert acme_business_case.status == 'in_review'


@pytest.mark.django_db
class TestBusinessCaseDeleteView:
    def test_post_deletes(self, acme_client, acme_business_case):
        pk = acme_business_case.pk
        url = reverse('initiation:businesscase_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not BusinessCase.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_business_case):
        pk = acme_business_case.pk
        url = reverse('initiation:businesscase_delete', args=[pk])
        acme_client.get(url)
        assert BusinessCase.objects.filter(pk=pk).exists()


# ===========================================================================
# ProjectCharter views
# ===========================================================================

@pytest.mark.django_db
class TestCharterListView:
    def test_200(self, acme_client, acme_charter):
        url = reverse('initiation:charter_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('initiation:charter_list')
        r = acme_client.get(url)
        assert 'initiation/charter_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client):
        url = reverse('initiation:charter_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'charters' in r.context
        assert 'status_choices' in r.context
        assert 'projects' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_charter, db, acme_tenant):
        other = ProjectCharter.objects.create(tenant=acme_tenant, title='Unrelated Charter')
        url = reverse('initiation:charter_list')
        r = acme_client.get(url, {'q': 'Portal'})
        pks = [obj.pk for obj in r.context['charters']]
        assert acme_charter.pk in pks
        assert other.pk not in pks

    def test_status_filter(self, acme_client, db, acme_tenant, acme_charter):
        active = ProjectCharter.objects.create(
            tenant=acme_tenant, title='Active Charter', status='active',
        )
        url = reverse('initiation:charter_list')
        r = acme_client.get(url, {'status': 'active'})
        pks = [obj.pk for obj in r.context['charters']]
        assert active.pk in pks
        assert acme_charter.pk not in pks  # acme_charter is 'draft'

    def test_pagination_max_10(self, acme_client, db, acme_tenant):
        for i in range(12):
            ProjectCharter.objects.create(tenant=acme_tenant, title=f'Charter {i:02d}')
        url = reverse('initiation:charter_list')
        r = acme_client.get(url)
        assert len(r.context['charters']) <= 10


@pytest.mark.django_db
class TestCharterDetailView:
    def test_200(self, acme_client, acme_charter):
        url = reverse('initiation:charter_detail', args=[acme_charter.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_var_is_charter(self, acme_client, acme_charter):
        url = reverse('initiation:charter_detail', args=[acme_charter.pk])
        r = acme_client.get(url)
        assert 'charter' in r.context
        assert r.context['charter'].pk == acme_charter.pk

    def test_detail_html_contains_number(self, acme_client, acme_charter):
        url = reverse('initiation:charter_detail', args=[acme_charter.pk])
        r = acme_client.get(url)
        assert acme_charter.number.encode() in r.content


@pytest.mark.django_db
class TestCharterCreateView:
    def test_get_form(self, acme_client):
        url = reverse('initiation:charter_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('initiation:charter_create')
        r = acme_client.post(url, {
            'title': 'New Charter',
            'objectives': 'Achieve goals',
            'scope_summary': '',
            'success_criteria': '',
            'start_date': '',
            'end_date': '',
            'budget': '0',
            'status': 'draft',
            'project': '',
            'sponsor': '',
            'project_manager': '',
        })
        assert r.status_code == 302
        obj = ProjectCharter.objects.filter(tenant=acme_tenant, title='New Charter').first()
        assert obj is not None
        assert obj.tenant == acme_tenant


@pytest.mark.django_db
class TestCharterEditView:
    def test_get_edit_form(self, acme_client, acme_charter):
        url = reverse('initiation:charter_edit', args=[acme_charter.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'charter' in r.context

    def test_post_updates(self, acme_client, acme_charter):
        url = reverse('initiation:charter_edit', args=[acme_charter.pk])
        r = acme_client.post(url, {
            'title': 'Updated Charter',
            'objectives': '',
            'scope_summary': '',
            'success_criteria': '',
            'start_date': '',
            'end_date': '',
            'budget': '0',
            'status': 'approved',
            'project': '',
            'sponsor': '',
            'project_manager': '',
        })
        assert r.status_code == 302
        acme_charter.refresh_from_db()
        assert acme_charter.title == 'Updated Charter'
        assert acme_charter.status == 'approved'


@pytest.mark.django_db
class TestCharterDeleteView:
    def test_post_deletes(self, acme_client, acme_charter):
        pk = acme_charter.pk
        url = reverse('initiation:charter_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not ProjectCharter.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_charter):
        pk = acme_charter.pk
        url = reverse('initiation:charter_delete', args=[pk])
        acme_client.get(url)
        assert ProjectCharter.objects.filter(pk=pk).exists()


# ===========================================================================
# Stakeholder views
# ===========================================================================

@pytest.mark.django_db
class TestStakeholderListView:
    def test_200(self, acme_client, acme_stakeholder):
        url = reverse('initiation:stakeholder_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('initiation:stakeholder_list')
        r = acme_client.get(url)
        assert 'initiation/stakeholder_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client):
        url = reverse('initiation:stakeholder_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'stakeholders' in r.context
        assert 'engagement_choices' in r.context
        assert 'level_choices' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_stakeholder, db, acme_tenant):
        other = Stakeholder.objects.create(
            tenant=acme_tenant, name='Bob Brown', organization='Other Corp',
        )
        url = reverse('initiation:stakeholder_list')
        r = acme_client.get(url, {'q': 'Alice'})
        pks = [obj.pk for obj in r.context['stakeholders']]
        assert acme_stakeholder.pk in pks
        assert other.pk not in pks

    def test_engagement_filter(self, acme_client, acme_stakeholder, db, acme_tenant):
        resistant = Stakeholder.objects.create(
            tenant=acme_tenant, name='Carl', engagement='resistant',
        )
        url = reverse('initiation:stakeholder_list')
        r = acme_client.get(url, {'engagement': 'resistant'})
        pks = [obj.pk for obj in r.context['stakeholders']]
        assert resistant.pk in pks
        assert acme_stakeholder.pk not in pks  # acme_stakeholder is 'supportive'

    def test_influence_filter(self, acme_client, acme_stakeholder, db, acme_tenant):
        low_influence = Stakeholder.objects.create(
            tenant=acme_tenant, name='Low Influence Person', influence='low',
        )
        url = reverse('initiation:stakeholder_list')
        r = acme_client.get(url, {'influence': 'low'})
        pks = [obj.pk for obj in r.context['stakeholders']]
        assert low_influence.pk in pks
        assert acme_stakeholder.pk not in pks  # acme_stakeholder is 'high'

    def test_pagination_max_10(self, acme_client, db, acme_tenant):
        for i in range(12):
            Stakeholder.objects.create(tenant=acme_tenant, name=f'Person {i:02d}')
        url = reverse('initiation:stakeholder_list')
        r = acme_client.get(url)
        assert len(r.context['stakeholders']) <= 10


@pytest.mark.django_db
class TestStakeholderDetailView:
    def test_200(self, acme_client, acme_stakeholder):
        url = reverse('initiation:stakeholder_detail', args=[acme_stakeholder.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_var_is_stakeholder(self, acme_client, acme_stakeholder):
        url = reverse('initiation:stakeholder_detail', args=[acme_stakeholder.pk])
        r = acme_client.get(url)
        assert 'stakeholder' in r.context
        assert r.context['stakeholder'].pk == acme_stakeholder.pk

    def test_detail_html_contains_name(self, acme_client, acme_stakeholder):
        url = reverse('initiation:stakeholder_detail', args=[acme_stakeholder.pk])
        r = acme_client.get(url)
        assert b'Alice Smith' in r.content


@pytest.mark.django_db
class TestStakeholderCreateView:
    def test_get_form(self, acme_client):
        url = reverse('initiation:stakeholder_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('initiation:stakeholder_create')
        r = acme_client.post(url, {
            'name': 'Dave Green',
            'organization': 'Acme',
            'role_title': 'CTO',
            'email': 'dave@acme.test',
            'influence': 'high',
            'interest': 'medium',
            'engagement': 'supportive',
            'communication_preference': '',
            'notes': '',
            'project': '',
        })
        assert r.status_code == 302
        obj = Stakeholder.objects.filter(tenant=acme_tenant, name='Dave Green').first()
        assert obj is not None
        assert obj.tenant == acme_tenant


@pytest.mark.django_db
class TestStakeholderEditView:
    def test_get_edit_form(self, acme_client, acme_stakeholder):
        url = reverse('initiation:stakeholder_edit', args=[acme_stakeholder.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'stakeholder' in r.context

    def test_post_updates(self, acme_client, acme_stakeholder):
        url = reverse('initiation:stakeholder_edit', args=[acme_stakeholder.pk])
        r = acme_client.post(url, {
            'name': 'Alice Updated',
            'organization': 'Acme Corp',
            'role_title': 'Executive Sponsor',
            'email': 'alice@acme.test',
            'influence': 'high',
            'interest': 'high',
            'engagement': 'leading',
            'communication_preference': '',
            'notes': '',
            'project': '',
        })
        assert r.status_code == 302
        acme_stakeholder.refresh_from_db()
        assert acme_stakeholder.name == 'Alice Updated'
        assert acme_stakeholder.engagement == 'leading'


@pytest.mark.django_db
class TestStakeholderDeleteView:
    def test_post_deletes(self, acme_client, acme_stakeholder):
        pk = acme_stakeholder.pk
        url = reverse('initiation:stakeholder_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not Stakeholder.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_stakeholder):
        pk = acme_stakeholder.pk
        url = reverse('initiation:stakeholder_delete', args=[pk])
        acme_client.get(url)
        assert Stakeholder.objects.filter(pk=pk).exists()


# ===========================================================================
# KickoffTask views
# ===========================================================================

@pytest.mark.django_db
class TestKickoffListView:
    def test_200(self, acme_client, acme_kickoff):
        url = reverse('initiation:kickoff_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('initiation:kickoff_list')
        r = acme_client.get(url)
        assert 'initiation/kickoff_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client):
        url = reverse('initiation:kickoff_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'kickoff_tasks' in r.context
        assert 'status_choices' in r.context
        assert 'category_choices' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_kickoff, db, acme_tenant):
        other = KickoffTask.objects.create(
            tenant=acme_tenant, title='Unrelated Task', category='team',
        )
        url = reverse('initiation:kickoff_list')
        r = acme_client.get(url, {'q': 'kickoff room'})
        pks = [obj.pk for obj in r.context['kickoff_tasks']]
        assert acme_kickoff.pk in pks
        assert other.pk not in pks

    def test_status_filter(self, acme_client, acme_kickoff, db, acme_tenant):
        done = KickoffTask.objects.create(
            tenant=acme_tenant, title='Done Task', status='done',
        )
        url = reverse('initiation:kickoff_list')
        r = acme_client.get(url, {'status': 'done'})
        pks = [obj.pk for obj in r.context['kickoff_tasks']]
        assert done.pk in pks
        assert acme_kickoff.pk not in pks  # acme_kickoff is 'pending'

    def test_category_filter(self, acme_client, acme_kickoff, db, acme_tenant):
        team_task = KickoffTask.objects.create(
            tenant=acme_tenant, title='Team Task', category='team',
        )
        url = reverse('initiation:kickoff_list')
        r = acme_client.get(url, {'category': 'team'})
        pks = [obj.pk for obj in r.context['kickoff_tasks']]
        assert team_task.pk in pks
        assert acme_kickoff.pk not in pks  # acme_kickoff is 'logistics'

    def test_pagination_max_10(self, acme_client, db, acme_tenant):
        for i in range(12):
            KickoffTask.objects.create(tenant=acme_tenant, title=f'Task {i:02d}')
        url = reverse('initiation:kickoff_list')
        r = acme_client.get(url)
        assert len(r.context['kickoff_tasks']) <= 10


@pytest.mark.django_db
class TestKickoffDetailView:
    def test_200(self, acme_client, acme_kickoff):
        url = reverse('initiation:kickoff_detail', args=[acme_kickoff.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_var_is_kickoff(self, acme_client, acme_kickoff):
        url = reverse('initiation:kickoff_detail', args=[acme_kickoff.pk])
        r = acme_client.get(url)
        assert 'kickoff' in r.context
        assert r.context['kickoff'].pk == acme_kickoff.pk

    def test_detail_html_contains_title(self, acme_client, acme_kickoff):
        url = reverse('initiation:kickoff_detail', args=[acme_kickoff.pk])
        r = acme_client.get(url)
        assert b'Book kickoff room' in r.content


@pytest.mark.django_db
class TestKickoffCreateView:
    def test_get_form(self, acme_client):
        url = reverse('initiation:kickoff_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('initiation:kickoff_create')
        r = acme_client.post(url, {
            'title': 'Send meeting invite',
            'description': '',
            'category': 'comms',
            'due_date': '',
            'status': 'pending',
            'is_complete': False,
            'project': '',
            'charter': '',
            'owner': '',
        })
        assert r.status_code == 302
        obj = KickoffTask.objects.filter(tenant=acme_tenant, title='Send meeting invite').first()
        assert obj is not None
        assert obj.tenant == acme_tenant


@pytest.mark.django_db
class TestKickoffEditView:
    def test_get_edit_form(self, acme_client, acme_kickoff):
        url = reverse('initiation:kickoff_edit', args=[acme_kickoff.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'kickoff' in r.context

    def test_post_updates(self, acme_client, acme_kickoff):
        url = reverse('initiation:kickoff_edit', args=[acme_kickoff.pk])
        r = acme_client.post(url, {
            'title': 'Updated kickoff task',
            'description': '',
            'category': 'governance',
            'due_date': '2026-08-01',
            'status': 'in_progress',
            'is_complete': False,
            'project': '',
            'charter': '',
            'owner': '',
        })
        assert r.status_code == 302
        acme_kickoff.refresh_from_db()
        assert acme_kickoff.title == 'Updated kickoff task'
        assert acme_kickoff.status == 'in_progress'


@pytest.mark.django_db
class TestKickoffDeleteView:
    def test_post_deletes(self, acme_client, acme_kickoff):
        pk = acme_kickoff.pk
        url = reverse('initiation:kickoff_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not KickoffTask.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_kickoff):
        pk = acme_kickoff.pk
        url = reverse('initiation:kickoff_delete', args=[pk])
        acme_client.get(url)
        assert KickoffTask.objects.filter(pk=pk).exists()


# ===========================================================================
# N+1 query guard
# ===========================================================================

@pytest.mark.django_db
def test_request_list_no_n_plus_1(acme_client, acme_tenant, django_assert_max_num_queries):
    """request_list with select_related should not issue more than ~10 queries."""
    for i in range(12):
        ProjectRequest.objects.create(
            tenant=acme_tenant, title=f'Request {i:02d}', priority='medium',
        )
    url = reverse('initiation:request_list')
    with django_assert_max_num_queries(10):
        r = acme_client.get(url)
    assert r.status_code == 200


@pytest.mark.django_db
def test_stakeholder_list_no_n_plus_1(acme_client, acme_tenant, django_assert_max_num_queries):
    """stakeholder_list should not issue more than ~10 queries."""
    for i in range(12):
        Stakeholder.objects.create(
            tenant=acme_tenant, name=f'Person {i:02d}',
        )
    url = reverse('initiation:stakeholder_list')
    with django_assert_max_num_queries(10):
        r = acme_client.get(url)
    assert r.status_code == 200
