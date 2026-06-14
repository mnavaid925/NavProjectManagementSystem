"""Tests for planning app forms: required fields, invalid input, tenant exclusion."""
import datetime

import pytest

from apps.planning.forms import (
    MilestoneForm,
    ScheduleBaselineForm,
    ScheduleTaskForm,
    TaskDependencyForm,
    WorkPackageForm,
)
from apps.planning.models import ScheduleTask, WorkPackage


# ---------------------------------------------------------------------------
# WorkPackageForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestWorkPackageForm:
    def test_valid_minimal(self, acme_tenant):
        form = WorkPackageForm(
            data={
                'code': '1.1',
                'name': 'Design',
                'project': '',
                'parent': '',
                'description': '',
                'level': '1',
                'estimated_effort_hours': '0',
                'owner': '',
                'status': 'not_started',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_name_required(self, acme_tenant):
        form = WorkPackageForm(
            data={
                'code': '1.1',
                'name': '',
                'project': '',
                'parent': '',
                'description': '',
                'level': '1',
                'estimated_effort_hours': '0',
                'owner': '',
                'status': 'not_started',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = WorkPackageForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_invalid_status(self, acme_tenant):
        form = WorkPackageForm(
            data={
                'code': '',
                'name': 'WP',
                'project': '',
                'parent': '',
                'description': '',
                'level': '1',
                'estimated_effort_hours': '0',
                'owner': '',
                'status': 'nonexistent_status',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors

    def test_parent_queryset_excludes_self(self, acme_tenant, acme_work_package):
        """When editing, the instance itself must not appear in parent dropdown."""
        form = WorkPackageForm(
            instance=acme_work_package,
            tenant=acme_tenant,
        )
        parent_qs = form.fields['parent'].queryset
        assert acme_work_package not in parent_qs

    def test_parent_queryset_includes_other_packages(self, acme_tenant, acme_work_package):
        """Another WP from same tenant should be available as parent."""
        other = WorkPackage.objects.create(tenant=acme_tenant, name='Other WP', code='2.0')
        form = WorkPackageForm(
            instance=acme_work_package,
            tenant=acme_tenant,
        )
        parent_qs = form.fields['parent'].queryset
        assert other in parent_qs

    def test_project_owner_parent_are_optional(self, acme_tenant):
        """project, parent, owner are not required."""
        form = WorkPackageForm(tenant=acme_tenant)
        assert form.fields['project'].required is False
        assert form.fields['parent'].required is False
        assert form.fields['owner'].required is False

    def test_invalid_effort_hours(self, acme_tenant):
        form = WorkPackageForm(
            data={
                'code': '',
                'name': 'WP',
                'project': '',
                'parent': '',
                'description': '',
                'level': '1',
                'estimated_effort_hours': 'not-a-number',
                'owner': '',
                'status': 'not_started',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'estimated_effort_hours' in form.errors


# ---------------------------------------------------------------------------
# ScheduleTaskForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestScheduleTaskForm:
    def test_valid_minimal(self, acme_tenant):
        form = ScheduleTaskForm(
            data={
                'name': 'My Task',
                'project': '',
                'work_package': '',
                'description': '',
                'assignee': '',
                'start_date': '',
                'end_date': '',
                'duration_days': '1',
                'effort_hours': '0',
                'estimate_method': 'bottom_up',
                'percent_complete': '0',
                'status': 'not_started',
                'is_critical': False,
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_name_required(self, acme_tenant):
        form = ScheduleTaskForm(
            data={
                'name': '',
                'project': '',
                'work_package': '',
                'description': '',
                'assignee': '',
                'start_date': '',
                'end_date': '',
                'duration_days': '1',
                'effort_hours': '0',
                'estimate_method': 'bottom_up',
                'percent_complete': '0',
                'status': 'not_started',
                'is_critical': False,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = ScheduleTaskForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_work_package_queryset_scoped_to_tenant(self, acme_tenant, acme_work_package, globex_work_package):
        form = ScheduleTaskForm(tenant=acme_tenant)
        qs = form.fields['work_package'].queryset
        assert acme_work_package in qs
        assert globex_work_package not in qs

    def test_project_work_package_assignee_optional(self, acme_tenant):
        form = ScheduleTaskForm(tenant=acme_tenant)
        assert form.fields['project'].required is False
        assert form.fields['work_package'].required is False
        assert form.fields['assignee'].required is False

    def test_invalid_estimate_method(self, acme_tenant):
        form = ScheduleTaskForm(
            data={
                'name': 'Task',
                'project': '',
                'work_package': '',
                'description': '',
                'assignee': '',
                'start_date': '',
                'end_date': '',
                'duration_days': '1',
                'effort_hours': '0',
                'estimate_method': 'invalid_method',
                'percent_complete': '0',
                'status': 'not_started',
                'is_critical': False,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'estimate_method' in form.errors

    def test_invalid_status(self, acme_tenant):
        form = ScheduleTaskForm(
            data={
                'name': 'Task',
                'project': '',
                'work_package': '',
                'description': '',
                'assignee': '',
                'start_date': '',
                'end_date': '',
                'duration_days': '1',
                'effort_hours': '0',
                'estimate_method': 'bottom_up',
                'percent_complete': '0',
                'status': 'bad_status',
                'is_critical': False,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors


# ---------------------------------------------------------------------------
# TaskDependencyForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTaskDependencyForm:
    def test_valid(self, acme_tenant, acme_task, acme_task2):
        form = TaskDependencyForm(
            data={
                'predecessor': acme_task.pk,
                'successor': acme_task2.pk,
                'dependency_type': 'FS',
                'lag_days': '0',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_predecessor_required(self, acme_tenant, acme_task2):
        form = TaskDependencyForm(
            data={
                'predecessor': '',
                'successor': acme_task2.pk,
                'dependency_type': 'FS',
                'lag_days': '0',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'predecessor' in form.errors

    def test_successor_required(self, acme_tenant, acme_task):
        form = TaskDependencyForm(
            data={
                'predecessor': acme_task.pk,
                'successor': '',
                'dependency_type': 'FS',
                'lag_days': '0',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'successor' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = TaskDependencyForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_notes_optional(self, acme_tenant):
        form = TaskDependencyForm(tenant=acme_tenant)
        assert form.fields['notes'].required is False

    def test_predecessor_queryset_scoped_to_tenant(
        self, acme_tenant, acme_task, globex_task
    ):
        form = TaskDependencyForm(tenant=acme_tenant)
        qs = form.fields['predecessor'].queryset
        assert acme_task in qs
        assert globex_task not in qs

    def test_successor_queryset_scoped_to_tenant(
        self, acme_tenant, acme_task, globex_task
    ):
        form = TaskDependencyForm(tenant=acme_tenant)
        qs = form.fields['successor'].queryset
        assert acme_task in qs
        assert globex_task not in qs

    def test_invalid_dependency_type(self, acme_tenant, acme_task, acme_task2):
        form = TaskDependencyForm(
            data={
                'predecessor': acme_task.pk,
                'successor': acme_task2.pk,
                'dependency_type': 'XX',
                'lag_days': '0',
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'dependency_type' in form.errors


# ---------------------------------------------------------------------------
# MilestoneForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMilestoneForm:
    def test_valid_minimal(self, acme_tenant):
        form = MilestoneForm(
            data={
                'name': 'Go Live',
                'project': '',
                'description': '',
                'due_date': '',
                'milestone_type': 'milestone',
                'gate_status': 'pending',
                'entry_criteria': '',
                'exit_criteria': '',
                'is_completed': False,
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_name_required(self, acme_tenant):
        form = MilestoneForm(
            data={
                'name': '',
                'project': '',
                'description': '',
                'due_date': '',
                'milestone_type': 'milestone',
                'gate_status': 'pending',
                'entry_criteria': '',
                'exit_criteria': '',
                'is_completed': False,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = MilestoneForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_project_optional(self, acme_tenant):
        form = MilestoneForm(tenant=acme_tenant)
        assert form.fields['project'].required is False

    def test_invalid_milestone_type(self, acme_tenant):
        form = MilestoneForm(
            data={
                'name': 'MS',
                'project': '',
                'description': '',
                'due_date': '',
                'milestone_type': 'bad_type',
                'gate_status': 'pending',
                'entry_criteria': '',
                'exit_criteria': '',
                'is_completed': False,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'milestone_type' in form.errors

    def test_invalid_gate_status(self, acme_tenant):
        form = MilestoneForm(
            data={
                'name': 'MS',
                'project': '',
                'description': '',
                'due_date': '',
                'milestone_type': 'milestone',
                'gate_status': 'bad_status',
                'entry_criteria': '',
                'exit_criteria': '',
                'is_completed': False,
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'gate_status' in form.errors


# ---------------------------------------------------------------------------
# ScheduleBaselineForm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestScheduleBaselineForm:
    def test_valid_minimal(self, acme_tenant):
        form = ScheduleBaselineForm(
            data={
                'name': 'BL v1',
                'project': '',
                'version': 'v1.0',
                'baseline_date': '',
                'planned_start': '',
                'planned_finish': '',
                'status': 'draft',
                'is_current': False,
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors

    def test_name_required(self, acme_tenant):
        form = ScheduleBaselineForm(
            data={
                'name': '',
                'project': '',
                'version': '',
                'baseline_date': '',
                'planned_start': '',
                'planned_finish': '',
                'status': 'draft',
                'is_current': False,
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_no_tenant_field(self, acme_tenant):
        form = ScheduleBaselineForm(tenant=acme_tenant)
        assert 'tenant' not in form.fields

    def test_project_optional(self, acme_tenant):
        form = ScheduleBaselineForm(tenant=acme_tenant)
        assert form.fields['project'].required is False

    def test_invalid_status(self, acme_tenant):
        form = ScheduleBaselineForm(
            data={
                'name': 'BL',
                'project': '',
                'version': '',
                'baseline_date': '',
                'planned_start': '',
                'planned_finish': '',
                'status': 'invalid_status',
                'is_current': False,
                'notes': '',
            },
            tenant=acme_tenant,
        )
        assert not form.is_valid()
        assert 'status' in form.errors

    def test_with_dates(self, acme_tenant):
        form = ScheduleBaselineForm(
            data={
                'name': 'BL with Dates',
                'project': '',
                'version': 'v2.0',
                'baseline_date': '2025-01-01',
                'planned_start': '2025-01-15',
                'planned_finish': '2025-06-30',
                'status': 'approved',
                'is_current': True,
                'notes': 'Approved baseline.',
            },
            tenant=acme_tenant,
        )
        assert form.is_valid(), form.errors
