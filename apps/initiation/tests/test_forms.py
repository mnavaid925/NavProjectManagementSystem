"""Tests for initiation app forms."""
import pytest

from apps.initiation.forms import (
    BusinessCaseForm,
    KickoffTaskForm,
    ProjectCharterForm,
    ProjectRequestForm,
    StakeholderForm,
)


# ---------------------------------------------------------------------------
# ProjectRequestForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProjectRequestForm:
    def test_valid_minimal(self, acme_tenant):
        form = ProjectRequestForm(
            data={
                'title': 'New Portal',
                'department': '',
                'description': '',
                'expected_benefit': '',
                'estimated_budget': '0',
                'priority': 'medium',
                'status': 'draft',
                'target_start_date': '',
                'requested_by': '',
                'project': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_title_required(self, acme_tenant):
        form = ProjectRequestForm(
            data={
                'title': '',
                'department': '',
                'estimated_budget': '0',
                'priority': 'medium',
                'status': 'draft',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_invalid_priority(self, acme_tenant):
        form = ProjectRequestForm(
            data={
                'title': 'Test',
                'estimated_budget': '0',
                'priority': 'galaxy_brain',
                'status': 'draft',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'priority' in form.errors

    def test_invalid_status(self, acme_tenant):
        form = ProjectRequestForm(
            data={
                'title': 'Test',
                'estimated_budget': '0',
                'priority': 'medium',
                'status': 'nonexistent',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = ProjectRequestForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_no_number_field(self, acme_tenant):
        form = ProjectRequestForm(tenant=acme_tenant)
        assert 'number' not in form.fields

    def test_requested_by_not_required(self, acme_tenant):
        form = ProjectRequestForm(tenant=acme_tenant)
        assert form.fields['requested_by'].required is False

    def test_project_not_required(self, acme_tenant):
        form = ProjectRequestForm(tenant=acme_tenant)
        assert form.fields['project'].required is False

    def test_requested_by_scoped_to_tenant(self, acme_tenant, acme_admin, globex_admin):
        form = ProjectRequestForm(tenant=acme_tenant)
        qs = form.fields['requested_by'].queryset
        assert acme_admin in qs
        assert globex_admin not in qs


# ---------------------------------------------------------------------------
# BusinessCaseForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestBusinessCaseForm:
    def test_valid_minimal(self, acme_tenant):
        form = BusinessCaseForm(
            data={
                'title': 'ERP Case',
                'summary': '',
                'problem_statement': '',
                'expected_roi': '0',
                'estimated_cost': '0',
                'estimated_benefit': '0',
                'payback_months': '0',
                'recommendation': 'go',
                'status': 'draft',
                'request': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_title_required(self, acme_tenant):
        form = BusinessCaseForm(
            data={
                'title': '',
                'expected_roi': '0',
                'estimated_cost': '0',
                'estimated_benefit': '0',
                'payback_months': '0',
                'recommendation': 'go',
                'status': 'draft',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_invalid_recommendation(self, acme_tenant):
        form = BusinessCaseForm(
            data={
                'title': 'Test',
                'expected_roi': '0',
                'estimated_cost': '0',
                'estimated_benefit': '0',
                'payback_months': '0',
                'recommendation': 'maybe',
                'status': 'draft',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'recommendation' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = BusinessCaseForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_no_number_field(self, acme_tenant):
        form = BusinessCaseForm(tenant=acme_tenant)
        assert 'number' not in form.fields

    def test_request_not_required(self, acme_tenant):
        form = BusinessCaseForm(tenant=acme_tenant)
        assert form.fields['request'].required is False

    def test_request_queryset_scoped_to_tenant(self, acme_tenant, acme_request, globex_request):
        form = BusinessCaseForm(tenant=acme_tenant)
        qs = form.fields['request'].queryset
        assert acme_request in qs
        assert globex_request not in qs


# ---------------------------------------------------------------------------
# ProjectCharterForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProjectCharterForm:
    def test_valid_minimal(self, acme_tenant):
        form = ProjectCharterForm(
            data={
                'title': 'New Charter',
                'objectives': '',
                'scope_summary': '',
                'success_criteria': '',
                'start_date': '',
                'end_date': '',
                'budget': '0',
                'status': 'draft',
                'project': '',
                'sponsor': '',
                'project_manager': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_title_required(self, acme_tenant):
        form = ProjectCharterForm(
            data={
                'title': '',
                'budget': '0',
                'status': 'draft',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_invalid_status(self, acme_tenant):
        form = ProjectCharterForm(
            data={
                'title': 'Test',
                'budget': '0',
                'status': 'nonexistent',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = ProjectCharterForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_no_number_field(self, acme_tenant):
        form = ProjectCharterForm(tenant=acme_tenant)
        assert 'number' not in form.fields

    def test_optional_fk_fields(self, acme_tenant):
        form = ProjectCharterForm(tenant=acme_tenant)
        assert form.fields['project'].required is False
        assert form.fields['sponsor'].required is False
        assert form.fields['project_manager'].required is False

    def test_sponsor_queryset_scoped_to_tenant(self, acme_tenant, acme_admin, globex_admin):
        form = ProjectCharterForm(tenant=acme_tenant)
        qs = form.fields['sponsor'].queryset
        assert acme_admin in qs
        assert globex_admin not in qs


# ---------------------------------------------------------------------------
# StakeholderForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStakeholderForm:
    def test_valid_minimal(self, acme_tenant):
        form = StakeholderForm(
            data={
                'name': 'Carol White',
                'organization': '',
                'role_title': '',
                'email': '',
                'influence': 'medium',
                'interest': 'medium',
                'engagement': 'neutral',
                'communication_preference': '',
                'notes': '',
                'project': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_name_required(self, acme_tenant):
        form = StakeholderForm(
            data={
                'name': '',
                'influence': 'medium',
                'interest': 'medium',
                'engagement': 'neutral',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_invalid_email(self, acme_tenant):
        form = StakeholderForm(
            data={
                'name': 'Test',
                'email': 'not-an-email',
                'influence': 'medium',
                'interest': 'medium',
                'engagement': 'neutral',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_invalid_engagement(self, acme_tenant):
        form = StakeholderForm(
            data={
                'name': 'Test',
                'influence': 'medium',
                'interest': 'medium',
                'engagement': 'very_enthusiastic',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'engagement' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = StakeholderForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_project_not_required(self, acme_tenant):
        form = StakeholderForm(tenant=acme_tenant)
        assert form.fields['project'].required is False


# ---------------------------------------------------------------------------
# KickoffTaskForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestKickoffTaskForm:
    def test_valid_minimal(self, acme_tenant):
        form = KickoffTaskForm(
            data={
                'title': 'Send invites',
                'description': '',
                'category': 'comms',
                'due_date': '',
                'status': 'pending',
                'is_complete': False,
                'project': '',
                'charter': '',
                'owner': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_title_required(self, acme_tenant):
        form = KickoffTaskForm(
            data={
                'title': '',
                'category': 'logistics',
                'status': 'pending',
                'is_complete': False,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_invalid_category(self, acme_tenant):
        form = KickoffTaskForm(
            data={
                'title': 'Test',
                'category': 'unknown_category',
                'status': 'pending',
                'is_complete': False,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'category' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = KickoffTaskForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_optional_fk_fields(self, acme_tenant):
        form = KickoffTaskForm(tenant=acme_tenant)
        assert form.fields['project'].required is False
        assert form.fields['charter'].required is False
        assert form.fields['owner'].required is False

    def test_charter_queryset_scoped_to_tenant(self, acme_tenant, acme_charter, globex_charter):
        form = KickoffTaskForm(tenant=acme_tenant)
        qs = form.fields['charter'].queryset
        assert acme_charter in qs
        assert globex_charter not in qs

    def test_owner_queryset_scoped_to_tenant(self, acme_tenant, acme_admin, globex_admin):
        form = KickoffTaskForm(tenant=acme_tenant)
        qs = form.fields['owner'].queryset
        assert acme_admin in qs
        assert globex_admin not in qs
