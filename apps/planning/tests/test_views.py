"""Tests for planning app views: CRUD, context keys, templates, pagination, N+1."""
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


# ===========================================================================
# Work Package views
# ===========================================================================

@pytest.mark.django_db
class TestWorkPackageListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('planning:workpackage_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('planning:workpackage_list')
        r = acme_client.get(url)
        assert 'planning/workpackage_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client, acme_work_package):
        url = reverse('planning:workpackage_list')
        r = acme_client.get(url)
        for key in ('page_obj', 'work_packages', 'status_choices', 'projects', 'total_count'):
            assert key in r.context, f"Missing context key: {key}"

    def test_search_by_name(self, acme_client, acme_work_package):
        url = reverse('planning:workpackage_list')
        r = acme_client.get(url, {'q': 'Acme WP Alpha'})
        names = [wp.name for wp in r.context['work_packages']]
        assert 'Acme WP Alpha' in names

    def test_search_excludes_non_matching(self, acme_client, acme_work_package, acme_tenant):
        WorkPackage.objects.create(tenant=acme_tenant, name='Other WP', code='9.9')
        url = reverse('planning:workpackage_list')
        r = acme_client.get(url, {'q': 'Acme WP Alpha'})
        names = [wp.name for wp in r.context['work_packages']]
        assert 'Other WP' not in names

    def test_status_filter(self, acme_client, acme_tenant):
        WorkPackage.objects.create(tenant=acme_tenant, name='InProgress WP', status='in_progress')
        WorkPackage.objects.create(tenant=acme_tenant, name='Done WP', status='completed')
        url = reverse('planning:workpackage_list')
        r = acme_client.get(url, {'status': 'in_progress'})
        statuses = [wp.status for wp in r.context['work_packages']]
        assert all(s == 'in_progress' for s in statuses)

    def test_pagination_size_10(self, acme_client, acme_tenant):
        for i in range(15):
            WorkPackage.objects.create(tenant=acme_tenant, name=f'WP {i:02d}', code=f'{i}')
        url = reverse('planning:workpackage_list')
        r = acme_client.get(url)
        assert len(r.context['work_packages']) <= 10


@pytest.mark.django_db
class TestWorkPackageDetailView:
    def test_200_for_owner(self, acme_client, acme_work_package):
        url = reverse('planning:workpackage_detail', args=[acme_work_package.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_work_package(self, acme_client, acme_work_package):
        url = reverse('planning:workpackage_detail', args=[acme_work_package.pk])
        r = acme_client.get(url)
        assert 'work_package' in r.context
        assert r.context['work_package'].pk == acme_work_package.pk

    def test_detail_html_contains_identifier(self, acme_client, acme_work_package):
        url = reverse('planning:workpackage_detail', args=[acme_work_package.pk])
        r = acme_client.get(url)
        assert b'Acme WP Alpha' in r.content


@pytest.mark.django_db
class TestWorkPackageCreateView:
    def test_get_form(self, acme_client):
        url = reverse('planning:workpackage_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('planning:workpackage_create')
        r = acme_client.post(url, {
            'code': '1.0',
            'name': 'New WP',
            'project': '',
            'parent': '',
            'description': '',
            'level': '1',
            'estimated_effort_hours': '8',
            'owner': '',
            'status': 'not_started',
        })
        assert r.status_code == 302
        obj = WorkPackage.objects.filter(tenant=acme_tenant, name='New WP').first()
        assert obj is not None
        assert obj.tenant == acme_tenant

    def test_post_does_not_create_for_other_tenant(self, acme_client, globex_tenant):
        url = reverse('planning:workpackage_create')
        acme_client.post(url, {
            'code': '1.0',
            'name': 'Should Not Exist',
            'project': '',
            'parent': '',
            'description': '',
            'level': '1',
            'estimated_effort_hours': '0',
            'owner': '',
            'status': 'not_started',
        })
        assert not WorkPackage.objects.filter(tenant=globex_tenant, name='Should Not Exist').exists()

    def test_invalid_post_rerenders_form(self, acme_client):
        url = reverse('planning:workpackage_create')
        r = acme_client.post(url, {
            'code': '',
            'name': '',  # required field missing
            'project': '',
            'parent': '',
            'description': '',
            'level': '1',
            'estimated_effort_hours': '0',
            'owner': '',
            'status': 'not_started',
        })
        assert r.status_code == 200
        assert 'form' in r.context


@pytest.mark.django_db
class TestWorkPackageEditView:
    def test_get_edit_form(self, acme_client, acme_work_package):
        url = reverse('planning:workpackage_edit', args=[acme_work_package.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'work_package' in r.context

    def test_post_updates_object(self, acme_client, acme_work_package):
        url = reverse('planning:workpackage_edit', args=[acme_work_package.pk])
        r = acme_client.post(url, {
            'code': '1.1',
            'name': 'Updated WP Name',
            'project': '',
            'parent': '',
            'description': 'Updated description',
            'level': '2',
            'estimated_effort_hours': '16',
            'owner': '',
            'status': 'in_progress',
        })
        assert r.status_code == 302
        acme_work_package.refresh_from_db()
        assert acme_work_package.name == 'Updated WP Name'
        assert acme_work_package.status == 'in_progress'


@pytest.mark.django_db
class TestWorkPackageDeleteView:
    def test_post_deletes(self, acme_client, acme_work_package):
        pk = acme_work_package.pk
        url = reverse('planning:workpackage_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not WorkPackage.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_work_package):
        pk = acme_work_package.pk
        url = reverse('planning:workpackage_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert WorkPackage.objects.filter(pk=pk).exists()


# ===========================================================================
# Schedule Task views
# ===========================================================================

@pytest.mark.django_db
class TestTaskListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('planning:task_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('planning:task_list')
        r = acme_client.get(url)
        assert 'planning/task_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client, acme_task):
        url = reverse('planning:task_list')
        r = acme_client.get(url)
        for key in ('page_obj', 'tasks', 'status_choices', 'estimate_method_choices',
                    'projects', 'total_count'):
            assert key in r.context, f"Missing context key: {key}"

    def test_search_by_name(self, acme_client, acme_task):
        url = reverse('planning:task_list')
        r = acme_client.get(url, {'q': 'Acme Task Alpha'})
        names = [t.name for t in r.context['tasks']]
        assert 'Acme Task Alpha' in names

    def test_status_filter(self, acme_client, acme_tenant):
        ScheduleTask.objects.create(
            tenant=acme_tenant, name='Blocked Task', status='blocked',
        )
        ScheduleTask.objects.create(
            tenant=acme_tenant, name='Not Started Task', status='not_started',
        )
        url = reverse('planning:task_list')
        r = acme_client.get(url, {'status': 'blocked'})
        statuses = [t.status for t in r.context['tasks']]
        assert all(s == 'blocked' for s in statuses)

    def test_estimate_method_filter(self, acme_client, acme_tenant):
        ScheduleTask.objects.create(
            tenant=acme_tenant, name='Analogous Task', estimate_method='analogous',
        )
        url = reverse('planning:task_list')
        r = acme_client.get(url, {'estimate_method': 'analogous'})
        methods = [t.estimate_method for t in r.context['tasks']]
        assert all(m == 'analogous' for m in methods)

    def test_pagination_size_10(self, acme_client, acme_tenant):
        for i in range(15):
            ScheduleTask.objects.create(tenant=acme_tenant, name=f'Task {i:02d}')
        url = reverse('planning:task_list')
        r = acme_client.get(url)
        assert len(r.context['tasks']) <= 10


@pytest.mark.django_db
class TestTaskDetailView:
    def test_200(self, acme_client, acme_task):
        url = reverse('planning:task_detail', args=[acme_task.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_task(self, acme_client, acme_task):
        url = reverse('planning:task_detail', args=[acme_task.pk])
        r = acme_client.get(url)
        assert 'task' in r.context
        assert r.context['task'].pk == acme_task.pk

    def test_detail_html_contains_name(self, acme_client, acme_task):
        url = reverse('planning:task_detail', args=[acme_task.pk])
        r = acme_client.get(url)
        assert b'Acme Task Alpha' in r.content


@pytest.mark.django_db
class TestTaskCreateView:
    def test_get_form(self, acme_client):
        url = reverse('planning:task_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('planning:task_create')
        r = acme_client.post(url, {
            'name': 'Brand New Task',
            'project': '',
            'work_package': '',
            'description': '',
            'assignee': '',
            'start_date': '',
            'end_date': '',
            'duration_days': '3',
            'effort_hours': '12',
            'estimate_method': 'bottom_up',
            'percent_complete': '0',
            'status': 'not_started',
            'is_critical': False,
        })
        assert r.status_code == 302
        obj = ScheduleTask.objects.filter(tenant=acme_tenant, name='Brand New Task').first()
        assert obj is not None
        assert obj.tenant == acme_tenant


@pytest.mark.django_db
class TestTaskEditView:
    def test_get_edit_form(self, acme_client, acme_task):
        url = reverse('planning:task_edit', args=[acme_task.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'task' in r.context

    def test_post_updates_object(self, acme_client, acme_task):
        url = reverse('planning:task_edit', args=[acme_task.pk])
        r = acme_client.post(url, {
            'name': 'Updated Task Name',
            'project': '',
            'work_package': '',
            'description': 'Updated',
            'assignee': '',
            'start_date': '2025-02-01',
            'end_date': '2025-02-15',
            'duration_days': '14',
            'effort_hours': '40',
            'estimate_method': 'three_point',
            'percent_complete': '50',
            'status': 'in_progress',
            'is_critical': True,
        })
        assert r.status_code == 302
        acme_task.refresh_from_db()
        assert acme_task.name == 'Updated Task Name'
        assert acme_task.status == 'in_progress'


@pytest.mark.django_db
class TestTaskDeleteView:
    def test_post_deletes(self, acme_client, acme_task):
        pk = acme_task.pk
        url = reverse('planning:task_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not ScheduleTask.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_task):
        pk = acme_task.pk
        url = reverse('planning:task_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert ScheduleTask.objects.filter(pk=pk).exists()


# ===========================================================================
# Task Dependency views
# ===========================================================================

@pytest.mark.django_db
class TestDependencyListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('planning:dependency_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('planning:dependency_list')
        r = acme_client.get(url)
        assert 'planning/dependency_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client, acme_dependency):
        url = reverse('planning:dependency_list')
        r = acme_client.get(url)
        for key in ('page_obj', 'dependencies', 'dependency_type_choices', 'total_count'):
            assert key in r.context, f"Missing context key: {key}"

    def test_search_by_predecessor_name(self, acme_client, acme_dependency):
        url = reverse('planning:dependency_list')
        r = acme_client.get(url, {'q': 'Acme Task Alpha'})
        assert acme_dependency in list(r.context['dependencies'])

    def test_dependency_type_filter(self, acme_client, acme_dependency, acme_tenant, acme_task, acme_task2):
        TaskDependency.objects.create(
            tenant=acme_tenant,
            predecessor=acme_task,
            successor=acme_task2,
            dependency_type='SS',
        )
        url = reverse('planning:dependency_list')
        r = acme_client.get(url, {'dependency_type': 'FS'})
        types = [d.dependency_type for d in r.context['dependencies']]
        assert all(t == 'FS' for t in types)

    def test_pagination_size_10(self, acme_client, acme_tenant):
        tasks = []
        for i in range(13):
            t = ScheduleTask.objects.create(tenant=acme_tenant, name=f'T{i}')
            tasks.append(t)
        # Create 12 dependencies between t0 and each subsequent task
        for i in range(1, 13):
            TaskDependency.objects.create(
                tenant=acme_tenant,
                predecessor=tasks[0],
                successor=tasks[i],
            )
        url = reverse('planning:dependency_list')
        r = acme_client.get(url)
        assert len(r.context['dependencies']) <= 10


@pytest.mark.django_db
class TestDependencyDetailView:
    def test_200(self, acme_client, acme_dependency):
        url = reverse('planning:dependency_detail', args=[acme_dependency.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_dependency(self, acme_client, acme_dependency):
        url = reverse('planning:dependency_detail', args=[acme_dependency.pk])
        r = acme_client.get(url)
        assert 'dependency' in r.context
        assert r.context['dependency'].pk == acme_dependency.pk

    def test_detail_html_contains_dependency_type(self, acme_client, acme_dependency):
        url = reverse('planning:dependency_detail', args=[acme_dependency.pk])
        r = acme_client.get(url)
        # The page should contain the dependency type or the task names
        assert b'FS' in r.content or b'Acme Task Alpha' in r.content


@pytest.mark.django_db
class TestDependencyCreateView:
    def test_get_form(self, acme_client):
        url = reverse('planning:dependency_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant, acme_task, acme_task2):
        url = reverse('planning:dependency_create')
        r = acme_client.post(url, {
            'predecessor': acme_task.pk,
            'successor': acme_task2.pk,
            'dependency_type': 'FF',
            'lag_days': '2',
            'notes': 'Test note',
        })
        assert r.status_code == 302
        dep = TaskDependency.objects.filter(
            tenant=acme_tenant,
            predecessor=acme_task,
            successor=acme_task2,
            dependency_type='FF',
        ).first()
        assert dep is not None


@pytest.mark.django_db
class TestDependencyEditView:
    def test_get_edit_form(self, acme_client, acme_dependency):
        url = reverse('planning:dependency_edit', args=[acme_dependency.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'dependency' in r.context

    def test_post_updates_object(self, acme_client, acme_dependency, acme_task, acme_task2):
        url = reverse('planning:dependency_edit', args=[acme_dependency.pk])
        r = acme_client.post(url, {
            'predecessor': acme_task.pk,
            'successor': acme_task2.pk,
            'dependency_type': 'SF',
            'lag_days': '5',
            'notes': 'Updated note',
        })
        assert r.status_code == 302
        acme_dependency.refresh_from_db()
        assert acme_dependency.dependency_type == 'SF'
        assert acme_dependency.lag_days == 5


@pytest.mark.django_db
class TestDependencyDeleteView:
    def test_post_deletes(self, acme_client, acme_dependency):
        pk = acme_dependency.pk
        url = reverse('planning:dependency_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not TaskDependency.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_dependency):
        pk = acme_dependency.pk
        url = reverse('planning:dependency_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert TaskDependency.objects.filter(pk=pk).exists()


# ===========================================================================
# Milestone views
# ===========================================================================

@pytest.mark.django_db
class TestMilestoneListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('planning:milestone_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('planning:milestone_list')
        r = acme_client.get(url)
        assert 'planning/milestone_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client, acme_milestone):
        url = reverse('planning:milestone_list')
        r = acme_client.get(url)
        for key in ('page_obj', 'milestones', 'milestone_type_choices',
                    'gate_status_choices', 'projects', 'total_count'):
            assert key in r.context, f"Missing context key: {key}"

    def test_search_by_name(self, acme_client, acme_milestone):
        url = reverse('planning:milestone_list')
        r = acme_client.get(url, {'q': 'Acme Milestone Alpha'})
        names = [ms.name for ms in r.context['milestones']]
        assert 'Acme Milestone Alpha' in names

    def test_milestone_type_filter(self, acme_client, acme_tenant, acme_milestone):
        Milestone.objects.create(
            tenant=acme_tenant, name='Gate PG', milestone_type='phase_gate',
        )
        url = reverse('planning:milestone_list')
        r = acme_client.get(url, {'milestone_type': 'milestone'})
        types = [ms.milestone_type for ms in r.context['milestones']]
        assert all(t == 'milestone' for t in types)

    def test_gate_status_filter(self, acme_client, acme_tenant):
        Milestone.objects.create(
            tenant=acme_tenant, name='Passed MS', gate_status='passed',
        )
        Milestone.objects.create(
            tenant=acme_tenant, name='Failed MS', gate_status='failed',
        )
        url = reverse('planning:milestone_list')
        r = acme_client.get(url, {'gate_status': 'passed'})
        statuses = [ms.gate_status for ms in r.context['milestones']]
        assert all(s == 'passed' for s in statuses)

    def test_pagination_size_10(self, acme_client, acme_tenant):
        for i in range(15):
            Milestone.objects.create(tenant=acme_tenant, name=f'MS {i:02d}')
        url = reverse('planning:milestone_list')
        r = acme_client.get(url)
        assert len(r.context['milestones']) <= 10


@pytest.mark.django_db
class TestMilestoneDetailView:
    def test_200(self, acme_client, acme_milestone):
        url = reverse('planning:milestone_detail', args=[acme_milestone.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_milestone(self, acme_client, acme_milestone):
        url = reverse('planning:milestone_detail', args=[acme_milestone.pk])
        r = acme_client.get(url)
        assert 'milestone' in r.context
        assert r.context['milestone'].pk == acme_milestone.pk

    def test_detail_html_contains_name(self, acme_client, acme_milestone):
        url = reverse('planning:milestone_detail', args=[acme_milestone.pk])
        r = acme_client.get(url)
        assert b'Acme Milestone Alpha' in r.content


@pytest.mark.django_db
class TestMilestoneCreateView:
    def test_get_form(self, acme_client):
        url = reverse('planning:milestone_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('planning:milestone_create')
        r = acme_client.post(url, {
            'name': 'New Milestone',
            'project': '',
            'description': '',
            'due_date': '2025-12-31',
            'milestone_type': 'phase_gate',
            'gate_status': 'pending',
            'entry_criteria': '',
            'exit_criteria': '',
            'is_completed': False,
        })
        assert r.status_code == 302
        obj = Milestone.objects.filter(tenant=acme_tenant, name='New Milestone').first()
        assert obj is not None
        assert obj.tenant == acme_tenant


@pytest.mark.django_db
class TestMilestoneEditView:
    def test_get_edit_form(self, acme_client, acme_milestone):
        url = reverse('planning:milestone_edit', args=[acme_milestone.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'milestone' in r.context

    def test_post_updates_object(self, acme_client, acme_milestone):
        url = reverse('planning:milestone_edit', args=[acme_milestone.pk])
        r = acme_client.post(url, {
            'name': 'Updated Milestone',
            'project': '',
            'description': 'Updated',
            'due_date': '2025-09-30',
            'milestone_type': 'phase_gate',
            'gate_status': 'passed',
            'entry_criteria': '',
            'exit_criteria': '',
            'is_completed': True,
        })
        assert r.status_code == 302
        acme_milestone.refresh_from_db()
        assert acme_milestone.name == 'Updated Milestone'
        assert acme_milestone.gate_status == 'passed'


@pytest.mark.django_db
class TestMilestoneDeleteView:
    def test_post_deletes(self, acme_client, acme_milestone):
        pk = acme_milestone.pk
        url = reverse('planning:milestone_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not Milestone.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_milestone):
        pk = acme_milestone.pk
        url = reverse('planning:milestone_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert Milestone.objects.filter(pk=pk).exists()


# ===========================================================================
# Schedule Baseline views
# ===========================================================================

@pytest.mark.django_db
class TestBaselineListView:
    def test_200_for_logged_in(self, acme_client):
        url = reverse('planning:baseline_list')
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_template_used(self, acme_client):
        url = reverse('planning:baseline_list')
        r = acme_client.get(url)
        assert 'planning/baseline_list.html' in [t.name for t in r.templates]

    def test_context_keys(self, acme_client, acme_baseline):
        url = reverse('planning:baseline_list')
        r = acme_client.get(url)
        for key in ('page_obj', 'baselines', 'status_choices', 'projects', 'total_count'):
            assert key in r.context, f"Missing context key: {key}"

    def test_search_by_name(self, acme_client, acme_baseline):
        url = reverse('planning:baseline_list')
        r = acme_client.get(url, {'q': 'Acme Baseline v1'})
        names = [b.name for b in r.context['baselines']]
        assert 'Acme Baseline v1' in names

    def test_status_filter(self, acme_client, acme_tenant):
        ScheduleBaseline.objects.create(
            tenant=acme_tenant, name='Draft BL', status='draft',
        )
        ScheduleBaseline.objects.create(
            tenant=acme_tenant, name='Approved BL', status='approved',
        )
        url = reverse('planning:baseline_list')
        r = acme_client.get(url, {'status': 'approved'})
        statuses = [b.status for b in r.context['baselines']]
        assert all(s == 'approved' for s in statuses)

    def test_pagination_size_10(self, acme_client, acme_tenant):
        for i in range(15):
            ScheduleBaseline.objects.create(
                tenant=acme_tenant, name=f'BL {i:02d}',
                baseline_date=datetime.date(2025, 1, i % 28 + 1),
            )
        url = reverse('planning:baseline_list')
        r = acme_client.get(url)
        assert len(r.context['baselines']) <= 10


@pytest.mark.django_db
class TestBaselineDetailView:
    def test_200(self, acme_client, acme_baseline):
        url = reverse('planning:baseline_detail', args=[acme_baseline.pk])
        r = acme_client.get(url)
        assert r.status_code == 200

    def test_context_has_baseline(self, acme_client, acme_baseline):
        url = reverse('planning:baseline_detail', args=[acme_baseline.pk])
        r = acme_client.get(url)
        assert 'baseline' in r.context
        assert r.context['baseline'].pk == acme_baseline.pk

    def test_detail_html_contains_name(self, acme_client, acme_baseline):
        url = reverse('planning:baseline_detail', args=[acme_baseline.pk])
        r = acme_client.get(url)
        assert b'Acme Baseline v1' in r.content


@pytest.mark.django_db
class TestBaselineCreateView:
    def test_get_form(self, acme_client):
        url = reverse('planning:baseline_create')
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context

    def test_post_creates_with_correct_tenant(self, acme_client, acme_tenant):
        url = reverse('planning:baseline_create')
        r = acme_client.post(url, {
            'name': 'New Baseline',
            'project': '',
            'version': 'v2.0',
            'baseline_date': '2025-06-01',
            'planned_start': '',
            'planned_finish': '',
            'status': 'draft',
            'is_current': False,
            'notes': '',
        })
        assert r.status_code == 302
        obj = ScheduleBaseline.objects.filter(tenant=acme_tenant, name='New Baseline').first()
        assert obj is not None
        assert obj.tenant == acme_tenant


@pytest.mark.django_db
class TestBaselineEditView:
    def test_get_edit_form(self, acme_client, acme_baseline):
        url = reverse('planning:baseline_edit', args=[acme_baseline.pk])
        r = acme_client.get(url)
        assert r.status_code == 200
        assert 'form' in r.context
        assert 'baseline' in r.context

    def test_post_updates_object(self, acme_client, acme_baseline):
        url = reverse('planning:baseline_edit', args=[acme_baseline.pk])
        r = acme_client.post(url, {
            'name': 'Updated Baseline',
            'project': '',
            'version': 'v1.1',
            'baseline_date': '2025-03-01',
            'planned_start': '',
            'planned_finish': '',
            'status': 'approved',
            'is_current': True,
            'notes': 'Updated.',
        })
        assert r.status_code == 302
        acme_baseline.refresh_from_db()
        assert acme_baseline.name == 'Updated Baseline'
        assert acme_baseline.status == 'approved'


@pytest.mark.django_db
class TestBaselineDeleteView:
    def test_post_deletes(self, acme_client, acme_baseline):
        pk = acme_baseline.pk
        url = reverse('planning:baseline_delete', args=[pk])
        r = acme_client.post(url)
        assert r.status_code == 302
        assert not ScheduleBaseline.objects.filter(pk=pk).exists()

    def test_get_does_not_delete(self, acme_client, acme_baseline):
        pk = acme_baseline.pk
        url = reverse('planning:baseline_delete', args=[pk])
        r = acme_client.get(url)
        assert r.status_code == 302
        assert ScheduleBaseline.objects.filter(pk=pk).exists()


# ===========================================================================
# Project-ID filter branches (covering views.py lines 42, 123, 355)
# ===========================================================================

@pytest.mark.django_db
def test_workpackage_list_project_filter(acme_client, acme_tenant):
    """Filtering by project_id= only shows WPs linked to that project."""
    from apps.projects.models import Project
    import datetime
    proj = Project.objects.create(
        tenant=acme_tenant, name='Alpha Project',
        start_date=datetime.date(2025, 1, 1),
    )
    wp_linked = WorkPackage.objects.create(
        tenant=acme_tenant, name='Linked WP', project=proj,
    )
    wp_other = WorkPackage.objects.create(
        tenant=acme_tenant, name='Unlinked WP',
    )
    url = reverse('planning:workpackage_list')
    r = acme_client.get(url, {'project': str(proj.pk)})
    pks = [wp.pk for wp in r.context['work_packages']]
    assert wp_linked.pk in pks
    assert wp_other.pk not in pks


@pytest.mark.django_db
def test_task_list_project_filter(acme_client, acme_tenant):
    """Filtering by project_id= only shows tasks linked to that project."""
    from apps.projects.models import Project
    import datetime
    proj = Project.objects.create(
        tenant=acme_tenant, name='Beta Project',
        start_date=datetime.date(2025, 1, 1),
    )
    task_linked = ScheduleTask.objects.create(
        tenant=acme_tenant, name='Linked Task', project=proj,
    )
    task_other = ScheduleTask.objects.create(
        tenant=acme_tenant, name='Unlinked Task',
    )
    url = reverse('planning:task_list')
    r = acme_client.get(url, {'project': str(proj.pk)})
    pks = [t.pk for t in r.context['tasks']]
    assert task_linked.pk in pks
    assert task_other.pk not in pks


@pytest.mark.django_db
def test_baseline_list_project_filter(acme_client, acme_tenant):
    """Filtering by project_id= only shows baselines linked to that project."""
    from apps.projects.models import Project
    import datetime
    proj = Project.objects.create(
        tenant=acme_tenant, name='Gamma Project',
        start_date=datetime.date(2025, 1, 1),
    )
    bl_linked = ScheduleBaseline.objects.create(
        tenant=acme_tenant, name='Linked BL', project=proj,
    )
    bl_other = ScheduleBaseline.objects.create(
        tenant=acme_tenant, name='Unlinked BL',
    )
    url = reverse('planning:baseline_list')
    r = acme_client.get(url, {'project': str(proj.pk)})
    pks = [b.pk for b in r.context['baselines']]
    assert bl_linked.pk in pks
    assert bl_other.pk not in pks


# ===========================================================================
# N+1 query guards
# ===========================================================================

@pytest.mark.django_db
def test_workpackage_list_no_n_plus_1(acme_client, acme_tenant, django_assert_max_num_queries):
    """workpackage_list should not issue more than ~10 queries regardless of count."""
    for i in range(12):
        WorkPackage.objects.create(tenant=acme_tenant, name=f'WP NQ {i}', code=str(i))
    url = reverse('planning:workpackage_list')
    with django_assert_max_num_queries(10):
        r = acme_client.get(url)
    assert r.status_code == 200


@pytest.mark.django_db
def test_task_list_no_n_plus_1(acme_client, acme_tenant, django_assert_max_num_queries):
    """task_list should not issue more than ~10 queries regardless of count."""
    for i in range(12):
        ScheduleTask.objects.create(tenant=acme_tenant, name=f'Task NQ {i}')
    url = reverse('planning:task_list')
    with django_assert_max_num_queries(10):
        r = acme_client.get(url)
    assert r.status_code == 200


@pytest.mark.django_db
def test_milestone_list_no_n_plus_1(acme_client, acme_tenant, django_assert_max_num_queries):
    """milestone_list should not issue more than ~10 queries regardless of count."""
    for i in range(12):
        Milestone.objects.create(tenant=acme_tenant, name=f'MS NQ {i}')
    url = reverse('planning:milestone_list')
    with django_assert_max_num_queries(10):
        r = acme_client.get(url)
    assert r.status_code == 200
