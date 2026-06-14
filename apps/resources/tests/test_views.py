"""Tests for resources app views: CRUD, context keys, templates, pagination."""
import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.resources.models import (
    Allocation,
    DemandForecast,
    Resource,
    Skill,
    TeamAssignment,
    TimeEntry,
)


# ===========================================================================
# Skills
# ===========================================================================
@pytest.mark.django_db
class TestSkillListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('resources:skill_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('resources:skill_list')
        r = acme_client.get(url)
        assert 'resources/skill_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client, acme_skill):
        url = reverse('resources:skill_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'skills' in r.context
        assert 'category_choices' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_tenant):
        Skill.objects.create(tenant=acme_tenant, name='Python', category='technical')
        Skill.objects.create(tenant=acme_tenant, name='Excel', category='functional')
        url = reverse('resources:skill_list')
        r = acme_client.get(url, {'q': 'Python'})
        names = [s.name for s in r.context['skills']]
        assert 'Python' in names
        assert 'Excel' not in names

    def test_category_filter(self, acme_client, acme_tenant):
        Skill.objects.create(tenant=acme_tenant, name='Skill A', category='technical')
        Skill.objects.create(tenant=acme_tenant, name='Skill B', category='soft')
        url = reverse('resources:skill_list')
        r = acme_client.get(url, {'category': 'technical'})
        for s in r.context['skills']:
            assert s.category == 'technical'

    def test_pagination_size_10(self, acme_client, acme_tenant):
        for i in range(15):
            Skill.objects.create(tenant=acme_tenant, name=f'Skill {i:02d}')
        url = reverse('resources:skill_list')
        r = acme_client.get(url)
        assert len(r.context['skills']) <= 10


@pytest.mark.django_db
class TestSkillDetailView:
    def test_200(self, acme_client, acme_skill):
        url = reverse('resources:skill_detail', args=[acme_skill.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_skill(self, acme_client, acme_skill):
        url = reverse('resources:skill_detail', args=[acme_skill.pk])
        r = acme_client.get(url)
        assert 'skill' in r.context
        assert r.context['skill'].pk == acme_skill.pk

    def test_detail_contains_skill_name(self, acme_client, acme_skill):
        url = reverse('resources:skill_detail', args=[acme_skill.pk])
        r = acme_client.get(url)
        assert acme_skill.name.encode() in r.content


@pytest.mark.django_db
class TestSkillCreateView:
    def test_get_form(self, acme_client):
        url = reverse('resources:skill_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_skill_for_correct_tenant(self, acme_client, acme_tenant):
        count_before = Skill.objects.filter(tenant=acme_tenant).count()
        url = reverse('resources:skill_create')
        r = acme_client.post(url, {
            'name': 'Rust',
            'category': 'technical',
            'description': '',
        })
        assert r.status_code == 302
        assert Skill.objects.filter(tenant=acme_tenant).count() == count_before + 1
        skill = Skill.objects.filter(tenant=acme_tenant, name='Rust').first()
        assert skill is not None
        assert skill.tenant == acme_tenant

    def test_invalid_post_shows_form_again(self, acme_client):
        url = reverse('resources:skill_create')
        r = acme_client.post(url, {'name': '', 'category': 'technical', 'description': ''})
        assert r.status_code == 200
        assert 'form' in r.context


@pytest.mark.django_db
class TestSkillEditView:
    def test_get_edit_form(self, acme_client, acme_skill):
        url = reverse('resources:skill_edit', args=[acme_skill.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'skill' in r.context

    def test_post_updates_skill(self, acme_client, acme_skill):
        url = reverse('resources:skill_edit', args=[acme_skill.pk])
        r = acme_client.post(url, {
            'name': 'Python 3',
            'category': 'technical',
            'description': 'Updated',
        })
        assert r.status_code == 302
        acme_skill.refresh_from_db()
        assert acme_skill.name == 'Python 3'


@pytest.mark.django_db
class TestSkillDeleteView:
    def test_post_deletes_skill(self, acme_client, acme_skill):
        pk = acme_skill.pk
        url = reverse('resources:skill_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not Skill.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_skill):
        pk = acme_skill.pk
        url = reverse('resources:skill_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert Skill.objects.filter(pk=pk).exists()


# ===========================================================================
# Resources
# ===========================================================================
@pytest.mark.django_db
class TestResourceListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('resources:resource_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('resources:resource_list')
        r = acme_client.get(url)
        assert 'resources/resource_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client):
        url = reverse('resources:resource_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'resources' in r.context
        assert 'resource_type_choices' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_tenant):
        Resource.objects.create(tenant=acme_tenant, name='Alice Dev', resource_type='employee')
        Resource.objects.create(tenant=acme_tenant, name='Bob Machine', resource_type='equipment')
        url = reverse('resources:resource_list')
        r = acme_client.get(url, {'q': 'Alice'})
        names = [res.name for res in r.context['resources']]
        assert 'Alice Dev' in names
        assert 'Bob Machine' not in names

    def test_resource_type_filter(self, acme_client, acme_tenant):
        Resource.objects.create(tenant=acme_tenant, name='Employee A', resource_type='employee')
        Resource.objects.create(tenant=acme_tenant, name='Machine X', resource_type='equipment')
        url = reverse('resources:resource_list')
        r = acme_client.get(url, {'resource_type': 'equipment'})
        for res in r.context['resources']:
            assert res.resource_type == 'equipment'

    def test_status_filter_active(self, acme_client, acme_tenant):
        Resource.objects.create(tenant=acme_tenant, name='Active', is_active=True)
        Resource.objects.create(tenant=acme_tenant, name='Inactive', is_active=False)
        url = reverse('resources:resource_list')
        r = acme_client.get(url, {'status': 'active'})
        for res in r.context['resources']:
            assert res.is_active is True

    def test_status_filter_inactive(self, acme_client, acme_tenant):
        Resource.objects.create(tenant=acme_tenant, name='Active B', is_active=True)
        Resource.objects.create(tenant=acme_tenant, name='Inactive B', is_active=False)
        url = reverse('resources:resource_list')
        r = acme_client.get(url, {'status': 'inactive'})
        for res in r.context['resources']:
            assert res.is_active is False

    def test_pagination_size_10(self, acme_client, acme_tenant):
        for i in range(15):
            Resource.objects.create(tenant=acme_tenant, name=f'Resource {i:02d}')
        url = reverse('resources:resource_list')
        r = acme_client.get(url)
        assert len(r.context['resources']) <= 10

    def test_resource_with_null_user_renders(self, acme_client, acme_resource_no_user):
        """A resource with user=None must not cause a 500 on the list view."""
        url = reverse('resources:resource_list')
        r = acme_client.get(url)
        assert r.status_code == 200
        names = [res.name for res in r.context['resources']]
        assert 'Bob Contractor' in names


@pytest.mark.django_db
class TestResourceDetailView:
    def test_200(self, acme_client, acme_resource):
        url = reverse('resources:resource_detail', args=[acme_resource.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_resource(self, acme_client, acme_resource):
        url = reverse('resources:resource_detail', args=[acme_resource.pk])
        r = acme_client.get(url)
        assert 'resource' in r.context
        assert r.context['resource'].pk == acme_resource.pk

    def test_detail_contains_resource_name(self, acme_client, acme_resource):
        url = reverse('resources:resource_detail', args=[acme_resource.pk])
        r = acme_client.get(url)
        assert acme_resource.name.encode() in r.content

    def test_resource_with_null_user_renders(self, acme_client, acme_resource_no_user):
        """Detail page for resource with user=None must not raise a 500."""
        url = reverse('resources:resource_detail', args=[acme_resource_no_user.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert acme_resource_no_user.name.encode() in r.content


@pytest.mark.django_db
class TestResourceCreateView:
    def test_get_form(self, acme_client):
        url = reverse('resources:resource_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_resource_for_correct_tenant(self, acme_client, acme_tenant):
        count_before = Resource.objects.filter(tenant=acme_tenant).count()
        url = reverse('resources:resource_create')
        r = acme_client.post(url, {
            'name': 'New Resource',
            'resource_type': 'employee',
            'email': '',
            'job_title': '',
            'department': '',
            'location': '',
            'capacity_hours_per_week': 40,
            'cost_rate': '0',
            'is_active': True,
        })
        assert r.status_code == 302
        assert Resource.objects.filter(tenant=acme_tenant).count() == count_before + 1
        res = Resource.objects.filter(tenant=acme_tenant, name='New Resource').first()
        assert res is not None
        assert res.tenant == acme_tenant

    def test_post_does_not_create_for_other_tenant(self, acme_client, globex_tenant):
        url = reverse('resources:resource_create')
        acme_client.post(url, {
            'name': 'Cross Tenant Resource',
            'resource_type': 'employee',
            'email': '',
            'job_title': '',
            'department': '',
            'location': '',
            'capacity_hours_per_week': 40,
            'cost_rate': '0',
            'is_active': True,
        })
        assert not Resource.objects.filter(tenant=globex_tenant, name='Cross Tenant Resource').exists()


@pytest.mark.django_db
class TestResourceEditView:
    def test_get_edit_form(self, acme_client, acme_resource):
        url = reverse('resources:resource_edit', args=[acme_resource.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'resource' in r.context

    def test_post_updates_resource(self, acme_client, acme_resource):
        url = reverse('resources:resource_edit', args=[acme_resource.pk])
        r = acme_client.post(url, {
            'name': 'Alice Senior Engineer',
            'resource_type': 'employee',
            'email': 'alice@acme.test',
            'job_title': 'Senior Software Engineer',
            'department': 'Engineering',
            'location': '',
            'capacity_hours_per_week': 40,
            'cost_rate': '90.00',
            'is_active': True,
        })
        assert r.status_code == 302
        acme_resource.refresh_from_db()
        assert acme_resource.name == 'Alice Senior Engineer'
        assert acme_resource.job_title == 'Senior Software Engineer'


@pytest.mark.django_db
class TestResourceDeleteView:
    def test_post_deletes_resource(self, acme_client, acme_resource):
        pk = acme_resource.pk
        url = reverse('resources:resource_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not Resource.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_resource):
        pk = acme_resource.pk
        url = reverse('resources:resource_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert Resource.objects.filter(pk=pk).exists()


# ===========================================================================
# Allocations
# ===========================================================================
@pytest.mark.django_db
class TestAllocationListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('resources:allocation_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('resources:allocation_list')
        r = acme_client.get(url)
        assert 'resources/allocation_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client):
        url = reverse('resources:allocation_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'allocations' in r.context
        assert 'status_choices' in r.context
        assert 'resources' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_allocation):
        url = reverse('resources:allocation_list')
        r = acme_client.get(url, {'q': 'Alice'})
        assert r.status_code == 200
        # If Alice is in allocations, it should appear
        pks = [a.pk for a in r.context['allocations']]
        assert acme_allocation.pk in pks

    def test_status_filter(self, acme_client, acme_tenant, acme_resource):
        Allocation.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            status='active', allocation_percent=100,
        )
        Allocation.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            status='planned', allocation_percent=50,
        )
        url = reverse('resources:allocation_list')
        r = acme_client.get(url, {'status': 'active'})
        for a in r.context['allocations']:
            assert a.status == 'active'

    def test_pagination_size_10(self, acme_client, acme_tenant, acme_resource):
        for i in range(15):
            Allocation.objects.create(
                tenant=acme_tenant, resource=acme_resource,
                allocation_percent=50,
            )
        url = reverse('resources:allocation_list')
        r = acme_client.get(url)
        assert len(r.context['allocations']) <= 10


@pytest.mark.django_db
class TestAllocationDetailView:
    def test_200(self, acme_client, acme_allocation):
        url = reverse('resources:allocation_detail', args=[acme_allocation.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_allocation(self, acme_client, acme_allocation):
        url = reverse('resources:allocation_detail', args=[acme_allocation.pk])
        r = acme_client.get(url)
        assert 'allocation' in r.context
        assert r.context['allocation'].pk == acme_allocation.pk

    def test_detail_contains_resource_name(self, acme_client, acme_allocation):
        url = reverse('resources:allocation_detail', args=[acme_allocation.pk])
        r = acme_client.get(url)
        # The __str__ includes resource name and percent
        assert b'Alice Engineer' in r.content


@pytest.mark.django_db
class TestAllocationCreateView:
    def test_get_form(self, acme_client):
        url = reverse('resources:allocation_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_allocation_for_correct_tenant(self, acme_client, acme_tenant, acme_resource):
        count_before = Allocation.objects.filter(tenant=acme_tenant).count()
        url = reverse('resources:allocation_create')
        r = acme_client.post(url, {
            'resource': acme_resource.pk,
            'project': '',
            'allocation_percent': 75,
            'allocated_hours': '30.00',
            'start_date': '2026-07-01',
            'end_date': '2026-09-30',
            'status': 'planned',
            'notes': '',
        })
        assert r.status_code == 302
        assert Allocation.objects.filter(tenant=acme_tenant).count() == count_before + 1
        alloc = Allocation.objects.filter(tenant=acme_tenant).order_by('-id').first()
        assert alloc.tenant == acme_tenant


@pytest.mark.django_db
class TestAllocationEditView:
    def test_get_edit_form(self, acme_client, acme_allocation):
        url = reverse('resources:allocation_edit', args=[acme_allocation.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'allocation' in r.context

    def test_post_updates_allocation(self, acme_client, acme_allocation, acme_resource):
        url = reverse('resources:allocation_edit', args=[acme_allocation.pk])
        r = acme_client.post(url, {
            'resource': acme_resource.pk,
            'project': '',
            'allocation_percent': 50,
            'allocated_hours': '20.00',
            'start_date': '2026-01-01',
            'end_date': '2026-03-31',
            'status': 'active',
            'notes': 'Updated',
        })
        assert r.status_code == 302
        acme_allocation.refresh_from_db()
        assert acme_allocation.status == 'active'
        assert acme_allocation.allocation_percent == 50


@pytest.mark.django_db
class TestAllocationDeleteView:
    def test_post_deletes_allocation(self, acme_client, acme_allocation):
        pk = acme_allocation.pk
        url = reverse('resources:allocation_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not Allocation.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_allocation):
        pk = acme_allocation.pk
        url = reverse('resources:allocation_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert Allocation.objects.filter(pk=pk).exists()


# ===========================================================================
# Team Assignments
# ===========================================================================
@pytest.mark.django_db
class TestAssignmentListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('resources:assignment_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client):
        url = reverse('resources:assignment_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'assignments' in r.context
        assert 'status_choices' in r.context
        assert 'projects' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_assignment):
        url = reverse('resources:assignment_list')
        r = acme_client.get(url, {'q': 'Lead Developer'})
        assert r.status_code == 200
        pks = [a.pk for a in r.context['assignments']]
        assert acme_assignment.pk in pks

    def test_status_filter(self, acme_client, acme_tenant, acme_resource):
        TeamAssignment.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            role_on_project='Dev A', status='proposed',
        )
        TeamAssignment.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            role_on_project='Dev B', status='released',
        )
        url = reverse('resources:assignment_list')
        r = acme_client.get(url, {'status': 'proposed'})
        for a in r.context['assignments']:
            assert a.status == 'proposed'

    def test_pagination_size_10(self, acme_client, acme_tenant, acme_resource):
        for i in range(15):
            TeamAssignment.objects.create(
                tenant=acme_tenant, resource=acme_resource,
                role_on_project=f'Role {i:02d}',
            )
        url = reverse('resources:assignment_list')
        r = acme_client.get(url)
        assert len(r.context['assignments']) <= 10


@pytest.mark.django_db
class TestAssignmentDetailView:
    def test_200(self, acme_client, acme_assignment):
        url = reverse('resources:assignment_detail', args=[acme_assignment.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_assignment(self, acme_client, acme_assignment):
        url = reverse('resources:assignment_detail', args=[acme_assignment.pk])
        r = acme_client.get(url)
        assert 'assignment' in r.context
        assert r.context['assignment'].pk == acme_assignment.pk

    def test_detail_contains_role_name(self, acme_client, acme_assignment):
        url = reverse('resources:assignment_detail', args=[acme_assignment.pk])
        r = acme_client.get(url)
        assert acme_assignment.role_on_project.encode() in r.content


@pytest.mark.django_db
class TestAssignmentCreateView:
    def test_get_form(self, acme_client):
        url = reverse('resources:assignment_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_assignment_for_correct_tenant(self, acme_client, acme_tenant, acme_resource):
        count_before = TeamAssignment.objects.filter(tenant=acme_tenant).count()
        url = reverse('resources:assignment_create')
        r = acme_client.post(url, {
            'resource': acme_resource.pk,
            'project': '',
            'role_on_project': 'Backend Developer',
            'is_lead': False,
            'start_date': '',
            'end_date': '',
            'status': 'active',
        })
        assert r.status_code == 302
        assert TeamAssignment.objects.filter(tenant=acme_tenant).count() == count_before + 1


@pytest.mark.django_db
class TestAssignmentEditView:
    def test_get_edit_form(self, acme_client, acme_assignment):
        url = reverse('resources:assignment_edit', args=[acme_assignment.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'assignment' in r.context

    def test_post_updates_assignment(self, acme_client, acme_assignment, acme_resource):
        url = reverse('resources:assignment_edit', args=[acme_assignment.pk])
        r = acme_client.post(url, {
            'resource': acme_resource.pk,
            'project': '',
            'role_on_project': 'Senior Lead',
            'is_lead': True,
            'start_date': '',
            'end_date': '',
            'status': 'released',
        })
        assert r.status_code == 302
        acme_assignment.refresh_from_db()
        assert acme_assignment.role_on_project == 'Senior Lead'
        assert acme_assignment.status == 'released'


@pytest.mark.django_db
class TestAssignmentDeleteView:
    def test_post_deletes(self, acme_client, acme_assignment):
        pk = acme_assignment.pk
        url = reverse('resources:assignment_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not TeamAssignment.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_assignment):
        pk = acme_assignment.pk
        url = reverse('resources:assignment_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert TeamAssignment.objects.filter(pk=pk).exists()


# ===========================================================================
# Demand Forecasts
# ===========================================================================
@pytest.mark.django_db
class TestForecastListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('resources:forecast_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_keys(self, acme_client):
        url = reverse('resources:forecast_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'forecasts' in r.context
        assert 'status_choices' in r.context
        assert 'skills' in r.context
        assert 'total_count' in r.context

    def test_search_filter(self, acme_client, acme_forecast):
        url = reverse('resources:forecast_list')
        r = acme_client.get(url, {'q': 'Q3 Python'})
        assert r.status_code == 200
        pks = [f.pk for f in r.context['forecasts']]
        assert acme_forecast.pk in pks

    def test_status_filter(self, acme_client, acme_tenant):
        DemandForecast.objects.create(
            tenant=acme_tenant, title='Proj', period='2026-07', status='projected'
        )
        DemandForecast.objects.create(
            tenant=acme_tenant, title='Conf', period='2026-08', status='confirmed'
        )
        url = reverse('resources:forecast_list')
        r = acme_client.get(url, {'status': 'projected'})
        for f in r.context['forecasts']:
            assert f.status == 'projected'

    def test_pagination_size_10(self, acme_client, acme_tenant):
        for i in range(15):
            DemandForecast.objects.create(
                tenant=acme_tenant, title=f'Forecast {i:02d}', period=f'2026-{i+1:02d}'
            )
        url = reverse('resources:forecast_list')
        r = acme_client.get(url)
        assert len(r.context['forecasts']) <= 10


@pytest.mark.django_db
class TestForecastDetailView:
    def test_200(self, acme_client, acme_forecast):
        url = reverse('resources:forecast_detail', args=[acme_forecast.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_forecast(self, acme_client, acme_forecast):
        url = reverse('resources:forecast_detail', args=[acme_forecast.pk])
        r = acme_client.get(url)
        assert 'forecast' in r.context
        assert r.context['forecast'].pk == acme_forecast.pk

    def test_detail_contains_forecast_title(self, acme_client, acme_forecast):
        url = reverse('resources:forecast_detail', args=[acme_forecast.pk])
        r = acme_client.get(url)
        assert acme_forecast.title.encode() in r.content


@pytest.mark.django_db
class TestForecastCreateView:
    def test_get_form(self, acme_client):
        url = reverse('resources:forecast_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_forecast_for_correct_tenant(self, acme_client, acme_tenant):
        count_before = DemandForecast.objects.filter(tenant=acme_tenant).count()
        url = reverse('resources:forecast_create')
        r = acme_client.post(url, {
            'title': 'New Forecast',
            'project': '',
            'skill': '',
            'period': '2026-11',
            'demand_hours': '100.00',
            'capacity_hours': '80.00',
            'status': 'projected',
            'notes': '',
        })
        assert r.status_code == 302
        assert DemandForecast.objects.filter(tenant=acme_tenant).count() == count_before + 1
        fc = DemandForecast.objects.filter(tenant=acme_tenant, title='New Forecast').first()
        assert fc is not None
        assert fc.tenant == acme_tenant


@pytest.mark.django_db
class TestForecastEditView:
    def test_get_edit_form(self, acme_client, acme_forecast):
        url = reverse('resources:forecast_edit', args=[acme_forecast.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'forecast' in r.context

    def test_post_updates_forecast(self, acme_client, acme_forecast):
        url = reverse('resources:forecast_edit', args=[acme_forecast.pk])
        r = acme_client.post(url, {
            'title': 'Updated Forecast',
            'project': '',
            'skill': '',
            'period': '2026-07',
            'demand_hours': '200.00',
            'capacity_hours': '150.00',
            'status': 'confirmed',
            'notes': 'Updated',
        })
        assert r.status_code == 302
        acme_forecast.refresh_from_db()
        assert acme_forecast.title == 'Updated Forecast'
        assert acme_forecast.status == 'confirmed'


@pytest.mark.django_db
class TestForecastDeleteView:
    def test_post_deletes(self, acme_client, acme_forecast):
        pk = acme_forecast.pk
        url = reverse('resources:forecast_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not DemandForecast.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_forecast):
        pk = acme_forecast.pk
        url = reverse('resources:forecast_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert DemandForecast.objects.filter(pk=pk).exists()


# ===========================================================================
# Time Entries
# ===========================================================================
@pytest.mark.django_db
class TestTimeEntryListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('resources:timeentry_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('resources:timeentry_list')
        r = acme_client.get(url)
        assert 'resources/timeentry_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client):
        url = reverse('resources:timeentry_list')
        r = acme_client.get(url)
        assert 'page_obj' in r.context
        assert 'time_entries' in r.context
        assert 'status_choices' in r.context
        assert 'resources' in r.context
        assert 'total_count' in r.context

    def test_search_filter_by_resource_name(self, acme_client, acme_time_entry):
        url = reverse('resources:timeentry_list')
        r = acme_client.get(url, {'q': 'Alice'})
        assert r.status_code == 200
        pks = [te.pk for te in r.context['time_entries']]
        assert acme_time_entry.pk in pks

    def test_search_filter_by_number(self, acme_client, acme_time_entry):
        url = reverse('resources:timeentry_list')
        r = acme_client.get(url, {'q': acme_time_entry.number})
        pks = [te.pk for te in r.context['time_entries']]
        assert acme_time_entry.pk in pks

    def test_status_filter(self, acme_client, acme_tenant, acme_resource):
        TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 1), hours=Decimal('8'), status='submitted',
        )
        TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 2), hours=Decimal('8'), status='approved',
        )
        url = reverse('resources:timeentry_list')
        r = acme_client.get(url, {'status': 'submitted'})
        for te in r.context['time_entries']:
            assert te.status == 'submitted'

    def test_pagination_size_10(self, acme_client, acme_tenant, acme_resource):
        for i in range(15):
            TimeEntry.objects.create(
                tenant=acme_tenant, resource=acme_resource,
                work_date=datetime.date(2026, 6, i + 1), hours=Decimal('8'),
            )
        url = reverse('resources:timeentry_list')
        r = acme_client.get(url)
        assert len(r.context['time_entries']) <= 10


@pytest.mark.django_db
class TestTimeEntryDetailView:
    def test_200(self, acme_client, acme_time_entry):
        url = reverse('resources:timeentry_detail', args=[acme_time_entry.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_timeentry(self, acme_client, acme_time_entry):
        url = reverse('resources:timeentry_detail', args=[acme_time_entry.pk])
        r = acme_client.get(url)
        assert 'timeentry' in r.context
        assert r.context['timeentry'].pk == acme_time_entry.pk

    def test_detail_contains_te_number(self, acme_client, acme_time_entry):
        url = reverse('resources:timeentry_detail', args=[acme_time_entry.pk])
        r = acme_client.get(url)
        assert acme_time_entry.number.encode() in r.content


@pytest.mark.django_db
class TestTimeEntryCreateView:
    def test_get_form(self, acme_client):
        url = reverse('resources:timeentry_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_time_entry_for_correct_tenant(self, acme_client, acme_tenant, acme_resource):
        count_before = TimeEntry.objects.filter(tenant=acme_tenant).count()
        url = reverse('resources:timeentry_create')
        r = acme_client.post(url, {
            'resource': acme_resource.pk,
            'project': '',
            'work_date': '2026-07-01',
            'hours': '6.00',
            'is_billable': True,
            'status': 'draft',
            'description': 'Test work',
        })
        assert r.status_code == 302
        assert TimeEntry.objects.filter(tenant=acme_tenant).count() == count_before + 1
        te = TimeEntry.objects.filter(tenant=acme_tenant).order_by('-id').first()
        assert te.tenant == acme_tenant
        assert te.number.startswith('TE-')

    def test_post_does_not_create_for_other_tenant(self, acme_client, globex_tenant, acme_resource):
        url = reverse('resources:timeentry_create')
        acme_client.post(url, {
            'resource': acme_resource.pk,
            'project': '',
            'work_date': '2026-07-01',
            'hours': '6.00',
            'is_billable': True,
            'status': 'draft',
            'description': '',
        })
        assert TimeEntry.objects.filter(tenant=globex_tenant).count() == 0


@pytest.mark.django_db
class TestTimeEntryEditView:
    def test_get_edit_form(self, acme_client, acme_time_entry):
        url = reverse('resources:timeentry_edit', args=[acme_time_entry.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'timeentry' in r.context

    def test_post_updates_time_entry(self, acme_client, acme_time_entry, acme_resource):
        url = reverse('resources:timeentry_edit', args=[acme_time_entry.pk])
        r = acme_client.post(url, {
            'resource': acme_resource.pk,
            'project': '',
            'work_date': '2026-06-01',
            'hours': '4.00',
            'is_billable': False,
            'status': 'submitted',
            'description': 'Half day',
        })
        assert r.status_code == 302
        acme_time_entry.refresh_from_db()
        assert acme_time_entry.status == 'submitted'
        assert acme_time_entry.hours == Decimal('4.00')


@pytest.mark.django_db
class TestTimeEntryDeleteView:
    def test_post_deletes(self, acme_client, acme_time_entry):
        pk = acme_time_entry.pk
        url = reverse('resources:timeentry_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not TimeEntry.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_time_entry):
        pk = acme_time_entry.pk
        url = reverse('resources:timeentry_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert TimeEntry.objects.filter(pk=pk).exists()


# ===========================================================================
# N+1 query guard
# ===========================================================================
@pytest.mark.django_db
def test_resource_list_no_n_plus_1(acme_client, acme_tenant, django_assert_max_num_queries):
    """resource_list should not issue more than ~12 queries regardless of row count."""
    for i in range(12):
        Resource.objects.create(
            tenant=acme_tenant,
            name=f'Worker {i:02d}',
            resource_type='employee',
        )
    url = reverse('resources:resource_list')
    with django_assert_max_num_queries(12):
        r = acme_client.get(url)
    assert r.status_code == 200


@pytest.mark.django_db
def test_timeentry_list_no_n_plus_1(acme_client, acme_tenant, acme_resource, django_assert_max_num_queries):
    """timeentry_list should not issue more than ~12 queries regardless of count."""
    for i in range(12):
        TimeEntry.objects.create(
            tenant=acme_tenant,
            resource=acme_resource,
            work_date=datetime.date(2026, 6, 1),
            hours=Decimal('8'),
        )
    url = reverse('resources:timeentry_list')
    with django_assert_max_num_queries(12):
        r = acme_client.get(url)
    assert r.status_code == 200


# ===========================================================================
# FK filter branches (covers uncovered view lines)
# ===========================================================================
@pytest.mark.django_db
def test_allocation_list_filter_by_resource_id(acme_client, acme_allocation, acme_resource, acme_tenant):
    """Allocation list filter ?resource=<id> (isdigit branch) should return matching rows."""
    url = reverse('resources:allocation_list')
    r = acme_client.get(url, {'resource': str(acme_resource.pk)})
    assert r.status_code == 200
    pks = [a.pk for a in r.context['allocations']]
    assert acme_allocation.pk in pks


@pytest.mark.django_db
def test_assignment_list_filter_by_project_id(acme_client, acme_assignment, acme_tenant):
    """Assignment list filter ?project=999 (isdigit branch) returns empty when no match."""
    url = reverse('resources:assignment_list')
    r = acme_client.get(url, {'project': '999999'})
    assert r.status_code == 200
    # No assignment links project 999999 — list should be empty
    assert len(r.context['assignments']) == 0


@pytest.mark.django_db
def test_forecast_list_filter_by_skill_id(acme_client, acme_forecast, acme_skill):
    """Forecast list filter ?skill=<id> (isdigit branch) should return matching rows."""
    url = reverse('resources:forecast_list')
    r = acme_client.get(url, {'skill': str(acme_skill.pk)})
    assert r.status_code == 200
    pks = [f.pk for f in r.context['forecasts']]
    assert acme_forecast.pk in pks


@pytest.mark.django_db
def test_timeentry_list_filter_by_resource_id(acme_client, acme_time_entry, acme_resource):
    """TimeEntry list filter ?resource=<id> (isdigit branch) should return matching rows."""
    url = reverse('resources:timeentry_list')
    r = acme_client.get(url, {'resource': str(acme_resource.pk)})
    assert r.status_code == 200
    pks = [te.pk for te in r.context['time_entries']]
    assert acme_time_entry.pk in pks
