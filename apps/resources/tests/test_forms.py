"""Tests for resources app forms: SkillForm, ResourceForm, AllocationForm,
TeamAssignmentForm, DemandForecastForm, TimeEntryForm."""
import datetime
from decimal import Decimal

import pytest

from apps.resources.forms import (
    AllocationForm,
    DemandForecastForm,
    ResourceForm,
    SkillForm,
    TeamAssignmentForm,
    TimeEntryForm,
)


# ---------------------------------------------------------------------------
# SkillForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSkillForm:
    def test_valid_minimal(self, acme_tenant):
        form = SkillForm(
            data={'name': 'Django', 'category': 'technical', 'description': ''},
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_valid_with_description(self, acme_tenant):
        form = SkillForm(
            data={'name': 'React', 'category': 'technical', 'description': 'Frontend framework'},
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_name_required(self, acme_tenant):
        form = SkillForm(
            data={'name': '', 'category': 'technical', 'description': ''},
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_invalid_category(self, acme_tenant):
        form = SkillForm(
            data={'name': 'Test', 'category': 'invalid_cat', 'description': ''},
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'category' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = SkillForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_all_categories_accepted(self, acme_tenant):
        for cat in ('technical', 'functional', 'soft', 'domain'):
            form = SkillForm(
                data={'name': f'Skill {cat}', 'category': cat, 'description': ''},
                tenant=acme_tenant,
            )
            assert form.is_valid(), f"Category '{cat}' should be valid: {form.errors}"


# ---------------------------------------------------------------------------
# ResourceForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestResourceForm:
    def test_valid_minimal(self, acme_tenant):
        form = ResourceForm(
            data={
                'name': 'Charlie Dev',
                'resource_type': 'employee',
                'email': '',
                'job_title': '',
                'department': '',
                'location': '',
                'capacity_hours_per_week': 40,
                'cost_rate': '0',
                'user': '',
                'skills': [],
                'is_active': True,
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_name_required(self, acme_tenant):
        form = ResourceForm(
            data={
                'name': '',
                'resource_type': 'employee',
                'email': '',
                'job_title': '',
                'department': '',
                'location': '',
                'capacity_hours_per_week': 40,
                'cost_rate': '0',
                'is_active': True,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = ResourceForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_user_field_is_not_required(self, acme_tenant):
        form = ResourceForm(tenant=acme_tenant)
        assert form.fields['user'].required is False

    def test_skills_field_is_not_required(self, acme_tenant):
        form = ResourceForm(tenant=acme_tenant)
        assert form.fields['skills'].required is False

    def test_user_queryset_scoped_to_tenant(self, acme_tenant, acme_admin, globex_admin):
        """User dropdown should only contain users from acme_tenant."""
        form = ResourceForm(tenant=acme_tenant)
        qs = form.fields['user'].queryset
        assert acme_admin in qs
        assert globex_admin not in qs

    def test_skills_queryset_scoped_to_tenant(self, acme_tenant, acme_skill, globex_skill):
        """Skills dropdown should only contain skills from acme_tenant."""
        form = ResourceForm(tenant=acme_tenant)
        qs = form.fields['skills'].queryset
        assert acme_skill in qs
        assert globex_skill not in qs

    def test_invalid_resource_type(self, acme_tenant):
        form = ResourceForm(
            data={
                'name': 'Bad Type',
                'resource_type': 'alien',
                'email': '',
                'job_title': '',
                'department': '',
                'location': '',
                'capacity_hours_per_week': 40,
                'cost_rate': '0',
                'is_active': True,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'resource_type' in form.errors

    def test_invalid_email(self, acme_tenant):
        form = ResourceForm(
            data={
                'name': 'Charlie',
                'resource_type': 'employee',
                'email': 'not-an-email',
                'job_title': '',
                'department': '',
                'location': '',
                'capacity_hours_per_week': 40,
                'cost_rate': '0',
                'is_active': True,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'email' in form.errors


# ---------------------------------------------------------------------------
# AllocationForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAllocationForm:
    def test_valid_minimal(self, acme_tenant, acme_resource):
        form = AllocationForm(
            data={
                'resource': acme_resource.pk,
                'project': '',
                'allocation_percent': 100,
                'allocated_hours': '0',
                'start_date': '',
                'end_date': '',
                'status': 'planned',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_resource_required(self, acme_tenant):
        form = AllocationForm(
            data={
                'resource': '',
                'project': '',
                'allocation_percent': 100,
                'allocated_hours': '0',
                'start_date': '',
                'end_date': '',
                'status': 'planned',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'resource' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = AllocationForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_project_not_required(self, acme_tenant):
        form = AllocationForm(tenant=acme_tenant)
        assert form.fields['project'].required is False

    def test_resource_queryset_scoped_to_tenant(self, acme_tenant, acme_resource, globex_resource):
        form = AllocationForm(tenant=acme_tenant)
        qs = form.fields['resource'].queryset
        assert acme_resource in qs
        assert globex_resource not in qs

    def test_invalid_status(self, acme_tenant, acme_resource):
        form = AllocationForm(
            data={
                'resource': acme_resource.pk,
                'project': '',
                'allocation_percent': 100,
                'allocated_hours': '0',
                'status': 'nonexistent',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors


# ---------------------------------------------------------------------------
# TeamAssignmentForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTeamAssignmentForm:
    def test_valid_minimal(self, acme_tenant, acme_resource):
        form = TeamAssignmentForm(
            data={
                'resource': acme_resource.pk,
                'project': '',
                'role_on_project': 'Developer',
                'is_lead': False,
                'start_date': '',
                'end_date': '',
                'status': 'active',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_resource_required(self, acme_tenant):
        form = TeamAssignmentForm(
            data={
                'resource': '',
                'project': '',
                'role_on_project': 'Developer',
                'is_lead': False,
                'status': 'active',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'resource' in form.errors

    def test_role_on_project_required(self, acme_tenant, acme_resource):
        form = TeamAssignmentForm(
            data={
                'resource': acme_resource.pk,
                'project': '',
                'role_on_project': '',
                'is_lead': False,
                'status': 'active',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'role_on_project' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = TeamAssignmentForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_project_not_required(self, acme_tenant):
        form = TeamAssignmentForm(tenant=acme_tenant)
        assert form.fields['project'].required is False

    def test_resource_queryset_scoped_to_tenant(self, acme_tenant, acme_resource, globex_resource):
        form = TeamAssignmentForm(tenant=acme_tenant)
        qs = form.fields['resource'].queryset
        assert acme_resource in qs
        assert globex_resource not in qs


# ---------------------------------------------------------------------------
# DemandForecastForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestDemandForecastForm:
    def test_valid_minimal(self, acme_tenant):
        form = DemandForecastForm(
            data={
                'title': 'Test Forecast',
                'project': '',
                'skill': '',
                'period': '2026-08',
                'demand_hours': '80.00',
                'capacity_hours': '80.00',
                'status': 'projected',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_title_required(self, acme_tenant):
        form = DemandForecastForm(
            data={
                'title': '',
                'project': '',
                'skill': '',
                'period': '2026-08',
                'demand_hours': '80.00',
                'capacity_hours': '80.00',
                'status': 'projected',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_period_required(self, acme_tenant):
        form = DemandForecastForm(
            data={
                'title': 'Test',
                'project': '',
                'skill': '',
                'period': '',
                'demand_hours': '0',
                'capacity_hours': '0',
                'status': 'projected',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'period' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = DemandForecastForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_project_not_required(self, acme_tenant):
        form = DemandForecastForm(tenant=acme_tenant)
        assert form.fields['project'].required is False

    def test_skill_not_required(self, acme_tenant):
        form = DemandForecastForm(tenant=acme_tenant)
        assert form.fields['skill'].required is False

    def test_skill_queryset_scoped_to_tenant(self, acme_tenant, acme_skill, globex_skill):
        form = DemandForecastForm(tenant=acme_tenant)
        qs = form.fields['skill'].queryset
        assert acme_skill in qs
        assert globex_skill not in qs

    def test_invalid_status(self, acme_tenant):
        form = DemandForecastForm(
            data={
                'title': 'Bad Status',
                'project': '',
                'skill': '',
                'period': '2026-08',
                'demand_hours': '0',
                'capacity_hours': '0',
                'status': 'unknown_status',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors


# ---------------------------------------------------------------------------
# TimeEntryForm
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTimeEntryForm:
    def test_valid_minimal(self, acme_tenant, acme_resource):
        form = TimeEntryForm(
            data={
                'resource': acme_resource.pk,
                'project': '',
                'work_date': '2026-06-01',
                'hours': '8.00',
                'is_billable': True,
                'status': 'draft',
                'description': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_resource_required(self, acme_tenant):
        form = TimeEntryForm(
            data={
                'resource': '',
                'project': '',
                'work_date': '2026-06-01',
                'hours': '8.00',
                'is_billable': True,
                'status': 'draft',
                'description': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'resource' in form.errors

    def test_work_date_required(self, acme_tenant, acme_resource):
        form = TimeEntryForm(
            data={
                'resource': acme_resource.pk,
                'project': '',
                'work_date': '',
                'hours': '8.00',
                'is_billable': True,
                'status': 'draft',
                'description': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'work_date' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = TimeEntryForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_no_number_field(self, acme_tenant):
        """auto-number must not appear in the form."""
        form = TimeEntryForm(tenant=acme_tenant)
        assert 'number' not in form.fields

    def test_project_not_required(self, acme_tenant):
        form = TimeEntryForm(tenant=acme_tenant)
        assert form.fields['project'].required is False

    def test_resource_queryset_scoped_to_tenant(self, acme_tenant, acme_resource, globex_resource):
        form = TimeEntryForm(tenant=acme_tenant)
        qs = form.fields['resource'].queryset
        assert acme_resource in qs
        assert globex_resource not in qs

    def test_invalid_status(self, acme_tenant, acme_resource):
        form = TimeEntryForm(
            data={
                'resource': acme_resource.pk,
                'project': '',
                'work_date': '2026-06-01',
                'hours': '8.00',
                'is_billable': True,
                'status': 'nonexistent',
                'description': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors

    def test_hours_invalid(self, acme_tenant, acme_resource):
        form = TimeEntryForm(
            data={
                'resource': acme_resource.pk,
                'project': '',
                'work_date': '2026-06-01',
                'hours': 'not-a-number',
                'is_billable': True,
                'status': 'draft',
                'description': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'hours' in form.errors
