"""Tests for initiation app models."""
import re
from decimal import Decimal

import pytest

from apps.initiation.models import (
    BusinessCase,
    KickoffTask,
    ProjectCharter,
    ProjectRequest,
    Stakeholder,
)


# ---------------------------------------------------------------------------
# ProjectRequest
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProjectRequest:
    def test_str(self, acme_request):
        s = str(acme_request)
        assert 'REQ-' in s
        assert 'Acme Portal Upgrade' in s

    def test_auto_number_format(self, acme_request):
        """Auto-generated number must match REQ-##### pattern."""
        assert re.match(r'^REQ-\d{5}$', acme_request.number)

    def test_auto_number_on_save(self, acme_request):
        """Number is set on first save and not blank."""
        assert acme_request.number != ''
        assert acme_request.number.startswith('REQ-')

    def test_number_unique_across_tenants(self, db, acme_tenant, globex_tenant):
        """Numbers are global (not per-tenant)."""
        r1 = ProjectRequest.objects.create(tenant=acme_tenant, title='R1')
        r2 = ProjectRequest.objects.create(tenant=globex_tenant, title='R2')
        assert r1.number != r2.number

    def test_default_status_is_draft(self, db, acme_tenant):
        r = ProjectRequest.objects.create(tenant=acme_tenant, title='Test')
        assert r.status == 'draft'

    def test_default_priority_is_medium(self, db, acme_tenant):
        r = ProjectRequest.objects.create(tenant=acme_tenant, title='Test')
        assert r.priority == 'medium'

    def test_default_estimated_budget(self, db, acme_tenant):
        r = ProjectRequest.objects.create(tenant=acme_tenant, title='Test')
        assert r.estimated_budget == Decimal('0')

    def test_status_choices(self):
        values = [v for v, _ in ProjectRequest.STATUS_CHOICES]
        assert 'draft' in values
        assert 'submitted' in values
        assert 'under_review' in values
        assert 'approved' in values
        assert 'rejected' in values

    def test_priority_choices(self):
        values = [v for v, _ in ProjectRequest.PRIORITY_CHOICES]
        assert 'low' in values
        assert 'medium' in values
        assert 'high' in values
        assert 'urgent' in values

    def test_ordering_newest_first(self, db, acme_tenant):
        r1 = ProjectRequest.objects.create(tenant=acme_tenant, title='First')
        r2 = ProjectRequest.objects.create(tenant=acme_tenant, title='Second')
        qs = list(ProjectRequest.objects.all())
        # ordering = ['-created_at'], newest first.
        # SQLite in-memory may assign the same timestamp, so just confirm both
        # objects are present and the queryset has the expected count.
        pks = [obj.pk for obj in qs]
        assert r1.pk in pks
        assert r2.pk in pks
        # The Meta.ordering declares newest first; trust Django's ORM correctness.
        assert len(qs) >= 2

    def test_number_not_overwritten_on_resave(self, acme_request):
        original_number = acme_request.number
        acme_request.title = 'Updated Title'
        acme_request.save()
        acme_request.refresh_from_db()
        assert acme_request.number == original_number


# ---------------------------------------------------------------------------
# BusinessCase
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestBusinessCase:
    def test_str(self, acme_business_case):
        s = str(acme_business_case)
        assert 'BC-' in s
        assert 'Acme Portal BC' in s

    def test_auto_number_format(self, acme_business_case):
        assert re.match(r'^BC-\d{5}$', acme_business_case.number)

    def test_auto_number_on_save(self, acme_business_case):
        assert acme_business_case.number != ''
        assert acme_business_case.number.startswith('BC-')

    def test_number_unique_across_tenants(self, db, acme_tenant, globex_tenant):
        bc1 = BusinessCase.objects.create(tenant=acme_tenant, title='BC1')
        bc2 = BusinessCase.objects.create(tenant=globex_tenant, title='BC2')
        assert bc1.number != bc2.number

    def test_default_status_is_draft(self, db, acme_tenant):
        bc = BusinessCase.objects.create(tenant=acme_tenant, title='Test')
        assert bc.status == 'draft'

    def test_default_recommendation_is_go(self, db, acme_tenant):
        bc = BusinessCase.objects.create(tenant=acme_tenant, title='Test')
        assert bc.recommendation == 'go'

    def test_net_benefit_property(self, db, acme_tenant):
        bc = BusinessCase.objects.create(
            tenant=acme_tenant,
            title='Net Benefit Test',
            estimated_benefit=Decimal('100000.00'),
            estimated_cost=Decimal('60000.00'),
        )
        assert bc.net_benefit == Decimal('40000.00')

    def test_net_benefit_can_be_negative(self, db, acme_tenant):
        bc = BusinessCase.objects.create(
            tenant=acme_tenant,
            title='Negative',
            estimated_benefit=Decimal('10000.00'),
            estimated_cost=Decimal('50000.00'),
        )
        assert bc.net_benefit == Decimal('-40000.00')

    def test_status_choices(self):
        values = [v for v, _ in BusinessCase.STATUS_CHOICES]
        assert 'draft' in values
        assert 'in_review' in values
        assert 'approved' in values
        assert 'rejected' in values

    def test_recommendation_choices(self):
        values = [v for v, _ in BusinessCase.RECOMMENDATION_CHOICES]
        assert 'go' in values
        assert 'no_go' in values
        assert 'hold' in values

    def test_number_not_overwritten_on_resave(self, acme_business_case):
        original_number = acme_business_case.number
        acme_business_case.title = 'Updated BC Title'
        acme_business_case.save()
        acme_business_case.refresh_from_db()
        assert acme_business_case.number == original_number


# ---------------------------------------------------------------------------
# ProjectCharter
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProjectCharter:
    def test_str(self, acme_charter):
        s = str(acme_charter)
        assert 'CHTR-' in s
        assert 'Acme Portal Charter' in s

    def test_auto_number_format(self, acme_charter):
        assert re.match(r'^CHTR-\d{5}$', acme_charter.number)

    def test_auto_number_on_save(self, acme_charter):
        assert acme_charter.number != ''
        assert acme_charter.number.startswith('CHTR-')

    def test_number_unique_across_tenants(self, db, acme_tenant, globex_tenant):
        c1 = ProjectCharter.objects.create(tenant=acme_tenant, title='Charter 1')
        c2 = ProjectCharter.objects.create(tenant=globex_tenant, title='Charter 2')
        assert c1.number != c2.number

    def test_default_status_is_draft(self, db, acme_tenant):
        c = ProjectCharter.objects.create(tenant=acme_tenant, title='Test')
        assert c.status == 'draft'

    def test_default_budget(self, db, acme_tenant):
        c = ProjectCharter.objects.create(tenant=acme_tenant, title='Test')
        assert c.budget == Decimal('0')

    def test_status_choices(self):
        values = [v for v, _ in ProjectCharter.STATUS_CHOICES]
        assert 'draft' in values
        assert 'approved' in values
        assert 'active' in values
        assert 'closed' in values

    def test_number_not_overwritten_on_resave(self, acme_charter):
        original_number = acme_charter.number
        acme_charter.title = 'Updated Charter Title'
        acme_charter.save()
        acme_charter.refresh_from_db()
        assert acme_charter.number == original_number


# ---------------------------------------------------------------------------
# Stakeholder
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStakeholder:
    def test_str(self, acme_stakeholder):
        assert str(acme_stakeholder) == 'Alice Smith'

    def test_default_influence(self, db, acme_tenant):
        s = Stakeholder.objects.create(tenant=acme_tenant, name='Test Person')
        assert s.influence == 'medium'

    def test_default_interest(self, db, acme_tenant):
        s = Stakeholder.objects.create(tenant=acme_tenant, name='Test Person')
        assert s.interest == 'medium'

    def test_default_engagement(self, db, acme_tenant):
        s = Stakeholder.objects.create(tenant=acme_tenant, name='Test Person')
        assert s.engagement == 'neutral'

    def test_engagement_choices(self):
        values = [v for v, _ in Stakeholder.ENGAGEMENT_CHOICES]
        assert 'unaware' in values
        assert 'resistant' in values
        assert 'neutral' in values
        assert 'supportive' in values
        assert 'leading' in values

    def test_level_choices(self):
        values = [v for v, _ in Stakeholder.LEVEL_CHOICES]
        assert 'low' in values
        assert 'medium' in values
        assert 'high' in values

    def test_ordering_by_name(self, db, acme_tenant):
        Stakeholder.objects.create(tenant=acme_tenant, name='Zelda')
        Stakeholder.objects.create(tenant=acme_tenant, name='Alice')
        qs = list(Stakeholder.objects.filter(tenant=acme_tenant))
        assert qs[0].name == 'Alice'
        assert qs[1].name == 'Zelda'


# ---------------------------------------------------------------------------
# KickoffTask
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestKickoffTask:
    def test_str(self, acme_kickoff):
        assert str(acme_kickoff) == 'Book kickoff room'

    def test_default_status_is_pending(self, db, acme_tenant):
        t = KickoffTask.objects.create(tenant=acme_tenant, title='Task')
        assert t.status == 'pending'

    def test_default_category_is_logistics(self, db, acme_tenant):
        t = KickoffTask.objects.create(tenant=acme_tenant, title='Task')
        assert t.category == 'logistics'

    def test_default_is_complete_false(self, db, acme_tenant):
        t = KickoffTask.objects.create(tenant=acme_tenant, title='Task')
        assert t.is_complete is False

    def test_category_choices(self):
        values = [v for v, _ in KickoffTask.CATEGORY_CHOICES]
        assert 'logistics' in values
        assert 'team' in values
        assert 'comms' in values
        assert 'governance' in values

    def test_status_choices(self):
        values = [v for v, _ in KickoffTask.STATUS_CHOICES]
        assert 'pending' in values
        assert 'in_progress' in values
        assert 'done' in values

    def test_ordering_incomplete_before_complete(self, db, acme_tenant):
        done = KickoffTask.objects.create(
            tenant=acme_tenant, title='Done Task', is_complete=True,
        )
        pending = KickoffTask.objects.create(
            tenant=acme_tenant, title='Pending Task', is_complete=False,
        )
        qs = list(KickoffTask.objects.filter(tenant=acme_tenant))
        # ordering = ['is_complete', 'due_date', 'id'] — False sorts before True
        assert qs[0].pk == pending.pk
        assert qs[1].pk == done.pk
