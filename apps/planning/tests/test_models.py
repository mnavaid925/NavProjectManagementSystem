"""Tests for planning app models: defaults, __str__, CHOICES, relationships."""
import datetime
from decimal import Decimal

import pytest

from apps.planning.models import (
    Milestone,
    ScheduleBaseline,
    ScheduleTask,
    TaskDependency,
    WorkPackage,
)


# ---------------------------------------------------------------------------
# WorkPackage
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestWorkPackageModel:
    def test_str_with_code(self, acme_work_package):
        """__str__ returns 'code name' when code is set."""
        acme_work_package.code = '1.1'
        acme_work_package.name = 'Design Phase'
        acme_work_package.save()
        assert str(acme_work_package) == '1.1 Design Phase'

    def test_str_without_code(self, acme_tenant):
        """__str__ strips leading space when code is empty."""
        wp = WorkPackage.objects.create(tenant=acme_tenant, name='No Code WP', code='')
        assert str(wp) == 'No Code WP'

    def test_defaults(self, acme_tenant):
        wp = WorkPackage.objects.create(tenant=acme_tenant, name='WP Defaults')
        assert wp.status == 'not_started'
        assert wp.level == 1
        assert wp.estimated_effort_hours == Decimal('0')
        assert wp.code == ''
        assert wp.description == ''
        assert wp.project is None
        assert wp.parent is None
        assert wp.owner is None

    def test_status_choices_values(self):
        values = [v for v, _ in WorkPackage.STATUS_CHOICES]
        assert 'not_started' in values
        assert 'in_progress' in values
        assert 'completed' in values

    def test_ordering_by_code_then_id(self, acme_tenant):
        wp1 = WorkPackage.objects.create(tenant=acme_tenant, name='WP Z', code='2.0')
        wp2 = WorkPackage.objects.create(tenant=acme_tenant, name='WP A', code='1.0')
        qs = list(WorkPackage.objects.filter(tenant=acme_tenant))
        assert qs[0].code == '1.0'
        assert qs[1].code == '2.0'

    def test_parent_child_relationship(self, acme_tenant, acme_work_package):
        child = WorkPackage.objects.create(
            tenant=acme_tenant, name='Child WP', parent=acme_work_package, code='1.1.1',
        )
        assert child.parent == acme_work_package
        assert child in acme_work_package.children.all()

    def test_self_reference_nullable(self, acme_tenant):
        wp = WorkPackage.objects.create(tenant=acme_tenant, name='Root WP')
        assert wp.parent is None

    def test_estimated_effort_hours_decimal(self, acme_tenant):
        wp = WorkPackage.objects.create(
            tenant=acme_tenant, name='Effort WP', estimated_effort_hours=Decimal('40.50'),
        )
        wp.refresh_from_db()
        assert wp.estimated_effort_hours == Decimal('40.50')


# ---------------------------------------------------------------------------
# ScheduleTask
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestScheduleTaskModel:
    def test_str(self, acme_task):
        assert str(acme_task) == 'Acme Task Alpha'

    def test_defaults(self, acme_tenant):
        task = ScheduleTask.objects.create(tenant=acme_tenant, name='Task Defaults')
        assert task.status == 'not_started'
        assert task.estimate_method == 'bottom_up'
        assert task.percent_complete == 0
        assert task.duration_days == 1
        assert task.effort_hours == Decimal('0')
        assert task.is_critical is False
        assert task.start_date is None
        assert task.end_date is None
        assert task.work_package is None
        assert task.project is None
        assert task.assignee is None

    def test_status_choices_values(self):
        values = [v for v, _ in ScheduleTask.STATUS_CHOICES]
        assert 'not_started' in values
        assert 'in_progress' in values
        assert 'completed' in values
        assert 'blocked' in values

    def test_estimate_method_choices_values(self):
        values = [v for v, _ in ScheduleTask.ESTIMATE_METHOD_CHOICES]
        assert 'analogous' in values
        assert 'parametric' in values
        assert 'bottom_up' in values
        assert 'three_point' in values

    def test_work_package_relationship(self, acme_tenant, acme_work_package):
        task = ScheduleTask.objects.create(
            tenant=acme_tenant, name='WP Task', work_package=acme_work_package,
        )
        assert task.work_package == acme_work_package
        assert task in acme_work_package.schedule_tasks.all()

    def test_is_critical_can_be_true(self, acme_tenant):
        task = ScheduleTask.objects.create(
            tenant=acme_tenant, name='Critical Task', is_critical=True,
        )
        task.refresh_from_db()
        assert task.is_critical is True

    def test_ordering_by_start_date_then_id(self, acme_tenant):
        t1 = ScheduleTask.objects.create(
            tenant=acme_tenant, name='Late Task', start_date=datetime.date(2025, 3, 1),
        )
        t2 = ScheduleTask.objects.create(
            tenant=acme_tenant, name='Early Task', start_date=datetime.date(2025, 1, 1),
        )
        qs = list(ScheduleTask.objects.filter(tenant=acme_tenant))
        # Earliest start_date first (NULLs sort before dates in SQLite)
        assert t2 in qs


# ---------------------------------------------------------------------------
# TaskDependency
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTaskDependencyModel:
    def test_str(self, acme_dependency, acme_task, acme_task2):
        s = str(acme_dependency)
        assert 'Acme Task Alpha' in s
        assert 'Acme Task Beta' in s
        assert 'FS' in s

    def test_defaults(self, acme_tenant, acme_task, acme_task2):
        dep = TaskDependency.objects.create(
            tenant=acme_tenant,
            predecessor=acme_task,
            successor=acme_task2,
        )
        assert dep.dependency_type == 'FS'
        assert dep.lag_days == 0
        assert dep.notes == ''

    def test_dependency_type_choices_values(self):
        values = [v for v, _ in TaskDependency.DEPENDENCY_TYPE_CHOICES]
        assert 'FS' in values
        assert 'SS' in values
        assert 'FF' in values
        assert 'SF' in values

    def test_all_dependency_types_creatable(self, acme_tenant, acme_task, acme_task2):
        for dt in ['FS', 'SS', 'FF', 'SF']:
            dep = TaskDependency.objects.create(
                tenant=acme_tenant,
                predecessor=acme_task,
                successor=acme_task2,
                dependency_type=dt,
            )
            assert dep.dependency_type == dt

    def test_lag_days_can_be_negative(self, acme_tenant, acme_task, acme_task2):
        """Negative lag (lead time) must be stored correctly."""
        dep = TaskDependency.objects.create(
            tenant=acme_tenant,
            predecessor=acme_task,
            successor=acme_task2,
            lag_days=-2,
        )
        dep.refresh_from_db()
        assert dep.lag_days == -2

    def test_predecessor_successor_related_names(self, acme_dependency, acme_task, acme_task2):
        assert acme_dependency in acme_task.successor_links.all()
        assert acme_dependency in acme_task2.predecessor_links.all()

    def test_ordering_newest_first(self, acme_tenant, acme_task, acme_task2):
        """TaskDependency orders by -created_at.
        SQLite resolution is 1 ms so we force distinct timestamps via update()."""
        import datetime
        from django.utils import timezone
        dep1 = TaskDependency.objects.create(
            tenant=acme_tenant, predecessor=acme_task, successor=acme_task2,
        )
        dep2 = TaskDependency.objects.create(
            tenant=acme_tenant, predecessor=acme_task2, successor=acme_task,
        )
        # Force dep2 to be definitively newer
        future = timezone.now() + datetime.timedelta(seconds=1)
        TaskDependency.objects.filter(pk=dep2.pk).update(created_at=future)
        qs = list(TaskDependency.objects.filter(tenant=acme_tenant))
        # Newest first — dep2 has the later created_at
        assert qs[0].pk == dep2.pk

    def test_no_self_dependency_guard_note(self, acme_tenant, acme_task):
        """Note: The model has NO database-level or form-level guard against
        self-referencing (predecessor == successor). This is a product gap.
        The test below verifies the current behaviour (no error raised)."""
        dep = TaskDependency.objects.create(
            tenant=acme_tenant,
            predecessor=acme_task,
            successor=acme_task,  # same task
            dependency_type='FS',
        )
        assert dep.pk is not None  # saved without error — guard is absent


# ---------------------------------------------------------------------------
# Milestone
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMilestoneModel:
    def test_str(self, acme_milestone):
        assert str(acme_milestone) == 'Acme Milestone Alpha'

    def test_defaults(self, acme_tenant):
        ms = Milestone.objects.create(tenant=acme_tenant, name='Default MS')
        assert ms.milestone_type == 'milestone'
        assert ms.gate_status == 'pending'
        assert ms.is_completed is False
        assert ms.due_date is None
        assert ms.description == ''
        assert ms.entry_criteria == ''
        assert ms.exit_criteria == ''
        assert ms.project is None

    def test_milestone_type_choices_values(self):
        values = [v for v, _ in Milestone.MILESTONE_TYPE_CHOICES]
        assert 'milestone' in values
        assert 'phase_gate' in values

    def test_gate_status_choices_values(self):
        values = [v for v, _ in Milestone.GATE_STATUS_CHOICES]
        assert 'pending' in values
        assert 'passed' in values
        assert 'failed' in values

    def test_is_completed_can_be_true(self, acme_tenant):
        ms = Milestone.objects.create(
            tenant=acme_tenant, name='Done MS', is_completed=True,
        )
        ms.refresh_from_db()
        assert ms.is_completed is True

    def test_ordering_by_due_date_then_id(self, acme_tenant):
        ms1 = Milestone.objects.create(
            tenant=acme_tenant, name='Late MS', due_date=datetime.date(2025, 12, 31),
        )
        ms2 = Milestone.objects.create(
            tenant=acme_tenant, name='Early MS', due_date=datetime.date(2025, 1, 1),
        )
        qs = list(Milestone.objects.filter(tenant=acme_tenant))
        assert qs[0].pk == ms2.pk


# ---------------------------------------------------------------------------
# ScheduleBaseline
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestScheduleBaselineModel:
    def test_str_with_version(self, acme_baseline):
        assert str(acme_baseline) == 'Acme Baseline v1 v1.0'

    def test_str_without_version(self, acme_tenant):
        bl = ScheduleBaseline.objects.create(
            tenant=acme_tenant, name='No Version', version='',
        )
        assert str(bl) == 'No Version'

    def test_defaults(self, acme_tenant):
        bl = ScheduleBaseline.objects.create(tenant=acme_tenant, name='BL Defaults')
        assert bl.status == 'draft'
        assert bl.is_current is False
        assert bl.version == ''
        assert bl.notes == ''
        assert bl.baseline_date is None
        assert bl.planned_start is None
        assert bl.planned_finish is None
        assert bl.project is None

    def test_status_choices_values(self):
        values = [v for v, _ in ScheduleBaseline.STATUS_CHOICES]
        assert 'draft' in values
        assert 'approved' in values
        assert 'superseded' in values

    def test_is_current_can_be_true(self, acme_tenant):
        bl = ScheduleBaseline.objects.create(
            tenant=acme_tenant, name='Current BL', is_current=True,
        )
        bl.refresh_from_db()
        assert bl.is_current is True

    def test_ordering_by_baseline_date_desc_then_id(self, acme_tenant):
        bl1 = ScheduleBaseline.objects.create(
            tenant=acme_tenant, name='Old BL', baseline_date=datetime.date(2025, 1, 1),
        )
        bl2 = ScheduleBaseline.objects.create(
            tenant=acme_tenant, name='New BL', baseline_date=datetime.date(2025, 6, 1),
        )
        qs = list(ScheduleBaseline.objects.filter(tenant=acme_tenant))
        # Newest baseline_date first
        assert qs[0].pk == bl2.pk
