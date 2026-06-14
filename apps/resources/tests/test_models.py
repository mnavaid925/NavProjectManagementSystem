"""Tests for resources app models: Skill, Resource, Allocation, TeamAssignment,
DemandForecast, TimeEntry."""
import datetime
import re
from decimal import Decimal

import pytest

from apps.resources.models import (
    Allocation,
    DemandForecast,
    Resource,
    Skill,
    TeamAssignment,
    TimeEntry,
)


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSkillModel:
    def test_str(self, acme_skill):
        assert str(acme_skill) == 'Python'

    def test_defaults(self, acme_tenant):
        skill = Skill.objects.create(tenant=acme_tenant, name='Go')
        assert skill.category == 'technical'
        assert skill.description == ''

    def test_category_choices(self):
        values = [v for v, _ in Skill.CATEGORY_CHOICES]
        assert 'technical' in values
        assert 'functional' in values
        assert 'soft' in values
        assert 'domain' in values

    def test_ordering_by_name(self, acme_tenant):
        Skill.objects.create(tenant=acme_tenant, name='Zebra Skill')
        Skill.objects.create(tenant=acme_tenant, name='Alpha Skill')
        names = list(Skill.objects.filter(tenant=acme_tenant).values_list('name', flat=True))
        assert names == sorted(names)

    def test_created_at_auto_set(self, acme_skill):
        assert acme_skill.created_at is not None

    def test_updated_at_auto_set(self, acme_skill):
        assert acme_skill.updated_at is not None

    def test_category_functional(self, acme_tenant):
        skill = Skill.objects.create(tenant=acme_tenant, name='Excel', category='functional')
        assert skill.category == 'functional'

    def test_category_soft(self, acme_tenant):
        skill = Skill.objects.create(tenant=acme_tenant, name='Leadership', category='soft')
        assert skill.category == 'soft'

    def test_category_domain(self, acme_tenant):
        skill = Skill.objects.create(tenant=acme_tenant, name='Finance', category='domain')
        assert skill.category == 'domain'


# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestResourceModel:
    def test_str(self, acme_resource):
        assert str(acme_resource) == 'Alice Engineer'

    def test_defaults(self, acme_tenant):
        resource = Resource.objects.create(tenant=acme_tenant, name='New Resource')
        assert resource.resource_type == 'employee'
        assert resource.email == ''
        assert resource.job_title == ''
        assert resource.department == ''
        assert resource.location == ''
        assert resource.capacity_hours_per_week == 40
        assert resource.cost_rate == Decimal('0')
        assert resource.user is None
        assert resource.is_active is True

    def test_resource_type_choices(self):
        values = [v for v, _ in Resource.RESOURCE_TYPE_CHOICES]
        assert 'employee' in values
        assert 'contractor' in values
        assert 'equipment' in values

    def test_user_nullable(self, acme_resource_no_user):
        """Resource with user=None must save without error."""
        assert acme_resource_no_user.user is None
        assert acme_resource_no_user.pk is not None

    def test_str_with_no_user(self, acme_resource_no_user):
        assert str(acme_resource_no_user) == 'Bob Contractor'

    def test_ordering_by_name(self, acme_tenant):
        Resource.objects.create(tenant=acme_tenant, name='Zebra Resource')
        Resource.objects.create(tenant=acme_tenant, name='Alpha Resource')
        names = list(Resource.objects.filter(tenant=acme_tenant).values_list('name', flat=True))
        assert names == sorted(names)

    def test_skills_m2m(self, acme_resource, acme_skill):
        acme_resource.skills.add(acme_skill)
        assert acme_skill in acme_resource.skills.all()

    def test_cost_rate_precision(self, acme_tenant):
        resource = Resource.objects.create(
            tenant=acme_tenant, name='Expensive', cost_rate=Decimal('125.50')
        )
        resource.refresh_from_db()
        assert resource.cost_rate == Decimal('125.50')

    def test_is_active_false(self, acme_tenant):
        resource = Resource.objects.create(
            tenant=acme_tenant, name='Inactive', is_active=False
        )
        assert resource.is_active is False

    def test_resource_type_contractor(self, acme_tenant):
        r = Resource.objects.create(
            tenant=acme_tenant, name='Contractor', resource_type='contractor'
        )
        assert r.resource_type == 'contractor'

    def test_resource_type_equipment(self, acme_tenant):
        r = Resource.objects.create(
            tenant=acme_tenant, name='Laptop', resource_type='equipment'
        )
        assert r.resource_type == 'equipment'


# ---------------------------------------------------------------------------
# Allocation
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAllocationModel:
    def test_str(self, acme_allocation):
        s = str(acme_allocation)
        assert 'Alice Engineer' in s
        assert '80%' in s

    def test_defaults(self, acme_tenant, acme_resource):
        alloc = Allocation.objects.create(tenant=acme_tenant, resource=acme_resource)
        assert alloc.allocation_percent == 100
        assert alloc.allocated_hours == Decimal('0')
        assert alloc.status == 'planned'
        assert alloc.start_date is None
        assert alloc.end_date is None
        assert alloc.notes == ''

    def test_status_choices(self):
        values = [v for v, _ in Allocation.STATUS_CHOICES]
        assert 'planned' in values
        assert 'active' in values
        assert 'completed' in values

    def test_is_overallocated_true(self, acme_tenant, acme_resource):
        alloc = Allocation.objects.create(
            tenant=acme_tenant, resource=acme_resource, allocation_percent=150
        )
        assert alloc.is_overallocated is True

    def test_is_overallocated_false_at_100(self, acme_tenant, acme_resource):
        alloc = Allocation.objects.create(
            tenant=acme_tenant, resource=acme_resource, allocation_percent=100
        )
        assert alloc.is_overallocated is False

    def test_is_overallocated_false_below_100(self, acme_allocation):
        # acme_allocation has 80%
        assert acme_allocation.is_overallocated is False

    def test_is_overallocated_boundary_101(self, acme_tenant, acme_resource):
        alloc = Allocation.objects.create(
            tenant=acme_tenant, resource=acme_resource, allocation_percent=101
        )
        assert alloc.is_overallocated is True

    def test_ordering(self, acme_tenant, acme_resource):
        a1 = Allocation.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            start_date=datetime.date(2026, 1, 1),
        )
        a2 = Allocation.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            start_date=datetime.date(2026, 6, 1),
        )
        qs = list(Allocation.objects.filter(tenant=acme_tenant))
        # Ordered by -start_date: newest start_date first
        assert qs[0].id == a2.id

    def test_project_nullable(self, acme_tenant, acme_resource):
        alloc = Allocation.objects.create(
            tenant=acme_tenant, resource=acme_resource, project=None
        )
        assert alloc.project is None


# ---------------------------------------------------------------------------
# TeamAssignment
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTeamAssignmentModel:
    def test_str(self, acme_assignment):
        s = str(acme_assignment)
        assert 'Alice Engineer' in s
        assert 'Lead Developer' in s

    def test_defaults(self, acme_tenant, acme_resource):
        ta = TeamAssignment.objects.create(
            tenant=acme_tenant,
            resource=acme_resource,
            role_on_project='Developer',
        )
        assert ta.is_lead is False
        assert ta.status == 'active'
        assert ta.start_date is None
        assert ta.end_date is None

    def test_status_choices(self):
        values = [v for v, _ in TeamAssignment.STATUS_CHOICES]
        assert 'proposed' in values
        assert 'active' in values
        assert 'released' in values

    def test_is_lead_true(self, acme_assignment):
        assert acme_assignment.is_lead is True

    def test_status_proposed(self, acme_tenant, acme_resource):
        ta = TeamAssignment.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            role_on_project='Tester', status='proposed',
        )
        assert ta.status == 'proposed'

    def test_status_released(self, acme_tenant, acme_resource):
        ta = TeamAssignment.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            role_on_project='Old Lead', status='released',
        )
        assert ta.status == 'released'

    def test_project_nullable(self, acme_tenant, acme_resource):
        ta = TeamAssignment.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            role_on_project='Analyst', project=None,
        )
        assert ta.project is None


# ---------------------------------------------------------------------------
# DemandForecast
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestDemandForecastModel:
    def test_str(self, acme_forecast):
        s = str(acme_forecast)
        assert 'Q3 Python Demand' in s
        assert '2026-07' in s

    def test_defaults(self, acme_tenant):
        forecast = DemandForecast.objects.create(
            tenant=acme_tenant, title='Test Forecast', period='2026-08'
        )
        assert forecast.demand_hours == Decimal('0')
        assert forecast.capacity_hours == Decimal('0')
        assert forecast.status == 'projected'
        assert forecast.notes == ''

    def test_status_choices(self):
        values = [v for v, _ in DemandForecast.STATUS_CHOICES]
        assert 'projected' in values
        assert 'confirmed' in values
        assert 'closed' in values

    def test_gap_hours_positive(self, acme_forecast):
        # demand 160, capacity 120 -> gap = 40
        assert acme_forecast.gap_hours == Decimal('40.00')

    def test_gap_hours_negative(self, acme_tenant):
        forecast = DemandForecast.objects.create(
            tenant=acme_tenant,
            title='Surplus',
            period='2026-09',
            demand_hours=Decimal('80.00'),
            capacity_hours=Decimal('120.00'),
        )
        assert forecast.gap_hours == Decimal('-40.00')

    def test_gap_hours_zero(self, acme_tenant):
        forecast = DemandForecast.objects.create(
            tenant=acme_tenant,
            title='Balanced',
            period='2026-10',
            demand_hours=Decimal('100.00'),
            capacity_hours=Decimal('100.00'),
        )
        assert forecast.gap_hours == Decimal('0.00')

    def test_ordering_by_period(self, acme_tenant):
        DemandForecast.objects.create(tenant=acme_tenant, title='Z', period='2026-12')
        DemandForecast.objects.create(tenant=acme_tenant, title='A', period='2026-01')
        forecasts = list(
            DemandForecast.objects.filter(tenant=acme_tenant).values_list('period', flat=True)
        )
        assert forecasts == sorted(forecasts)

    def test_status_confirmed(self, acme_tenant):
        f = DemandForecast.objects.create(
            tenant=acme_tenant, title='Confirmed', period='2027-01', status='confirmed'
        )
        assert f.status == 'confirmed'

    def test_project_and_skill_nullable(self, acme_tenant):
        f = DemandForecast.objects.create(
            tenant=acme_tenant, title='No Links', period='2027-02',
            project=None, skill=None,
        )
        assert f.project is None
        assert f.skill is None


# ---------------------------------------------------------------------------
# TimeEntry
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTimeEntryModel:
    def test_str(self, acme_time_entry):
        s = str(acme_time_entry)
        assert acme_time_entry.number in s
        assert 'Alice Engineer' in s

    def test_auto_number_format(self, acme_time_entry):
        assert re.match(r'^TE-\d{5}$', acme_time_entry.number), (
            f"Expected TE-##### format, got: {acme_time_entry.number}"
        )

    def test_auto_number_length(self, acme_time_entry):
        assert len(acme_time_entry.number) == 8  # TE-#####

    def test_auto_number_unique(self, acme_tenant, acme_resource):
        te1 = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 1), hours=Decimal('4.00'),
        )
        te2 = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 2), hours=Decimal('6.00'),
        )
        assert te1.number != te2.number

    def test_auto_number_not_overwritten_on_save(self, acme_time_entry):
        original_number = acme_time_entry.number
        acme_time_entry.description = 'Updated'
        acme_time_entry.save()
        acme_time_entry.refresh_from_db()
        assert acme_time_entry.number == original_number

    def test_defaults(self, acme_tenant, acme_resource):
        te = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 3),
        )
        assert te.hours == Decimal('0')
        assert te.is_billable is True
        assert te.status == 'draft'
        assert te.description == ''

    def test_status_choices(self):
        values = [v for v, _ in TimeEntry.STATUS_CHOICES]
        assert 'draft' in values
        assert 'submitted' in values
        assert 'approved' in values
        assert 'rejected' in values

    def test_status_submitted(self, acme_tenant, acme_resource):
        te = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 4), status='submitted',
        )
        assert te.status == 'submitted'

    def test_status_approved(self, acme_tenant, acme_resource):
        te = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 5), status='approved',
        )
        assert te.status == 'approved'

    def test_status_rejected(self, acme_tenant, acme_resource):
        te = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 6), status='rejected',
        )
        assert te.status == 'rejected'

    def test_ordering_newest_work_date_first(self, acme_tenant, acme_resource):
        te1 = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 1, 1), hours=Decimal('8'),
        )
        te2 = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 1), hours=Decimal('8'),
        )
        entries = list(TimeEntry.objects.filter(tenant=acme_tenant))
        # Ordered by -work_date: most recent first
        assert entries[0].id == te2.id

    def test_project_nullable(self, acme_tenant, acme_resource):
        te = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 7), project=None,
        )
        assert te.project is None

    def test_is_billable_false(self, acme_tenant, acme_resource):
        te = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 6, 8), is_billable=False,
        )
        assert te.is_billable is False

    def test_number_collision_avoidance(self, acme_tenant, acme_resource):
        """When the candidate number already exists, _generate_number loops to the next seq."""
        # Create a TimeEntry normally to get TE-00001
        te1 = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 7, 1), hours=Decimal('8'),
        )
        # Manually jam the NEXT expected number into an existing entry so the loop fires
        # (seq would be te1.id+1; we pre-occupy that slot)
        next_seq = te1.id + 1
        collision_number = f'TE-{next_seq:05d}'
        # Create directly via objects.create but give it an explicit number to simulate collision
        te_collision = TimeEntry(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 7, 2), hours=Decimal('2'),
            number=collision_number,
        )
        te_collision.save.__func__  # just access, don't call — we bypass _generate_number
        # Use raw super().save to avoid regenerating the number
        from django.db.models import Model
        Model.save(te_collision)

        # Now creating a new TimeEntry should skip the colliding number
        te2 = TimeEntry.objects.create(
            tenant=acme_tenant, resource=acme_resource,
            work_date=datetime.date(2026, 7, 3), hours=Decimal('4'),
        )
        assert te2.number != collision_number
        assert te2.number.startswith('TE-')
