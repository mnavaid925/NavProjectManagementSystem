"""Seed idempotent demo data for the Time & Attendance Tracking module.

Creates timesheets and their daily lines, timesheet approvals, leave records,
and utilization snapshots for the acme and globex tenants. Safe to run
repeatedly: each tenant is guarded by an existence check on Timesheet, and
auto-numbered records use an existence-checked number helper.

Usage:
    python manage.py seed_timesheets
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.timesheets.models import (
    LeaveRecord,
    Timesheet,
    TimesheetApproval,
    TimesheetLine,
    UtilizationSnapshot,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

TIMESHEET_STATUSES = ['draft', 'submitted', 'approved', 'rejected']
ACTIVITIES = ['development', 'meeting', 'review', 'admin', 'support', 'research']
DECISIONS = ['pending', 'approved', 'rejected', 'returned']
LEAVE_TYPES = ['annual', 'sick', 'unpaid', 'parental', 'bereavement', 'toil']
LEAVE_STATUSES = ['requested', 'approved', 'rejected', 'cancelled']
PERIODS = ['2026-05', '2026-06']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Time & Attendance Tracking module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Timesheet.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (timesheets) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding timesheets for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            timesheets = self._seed_timesheets(tenant, members, projects)
            lines = self._seed_lines(tenant, timesheets, projects)
            approvals = self._seed_approvals(tenant, timesheets, members)
            leave_records = self._seed_leave(tenant, members)
            snapshots = self._seed_snapshots(tenant, members, projects)

            self.stdout.write(self.style.SUCCESS(
                f'    Timesheets: {len(timesheets)}  Lines: {len(lines)}  '
                f'Approvals: {len(approvals)}  Leave records: {len(leave_records)}  '
                f'Snapshots: {len(snapshots)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nTimesheets seed complete.'))
        self.stdout.write(self.style.WARNING(
            '  Reminder: log in as a tenant admin to see data - '
            'admin_acme / admin_globex (password123). '
            'The "admin" superuser has tenant=None and will see nothing.'
        ))

    # ---------------------------------------------------------- number helper
    @staticmethod
    def _next_number(model, prefix):
        last = model.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'{prefix}-{seq:05d}'
        while model.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'{prefix}-{seq:05d}'
        return candidate

    # ------------------------------------------------------------- timesheets
    def _seed_timesheets(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(Timesheet, 'TS')
            if Timesheet.objects.filter(number=number).exists():
                continue
            # weekly windows in the last 8 weeks
            period_start = today - timedelta(weeks=(i + 1), days=today.weekday())
            period_end = period_start + timedelta(days=6)
            status = TIMESHEET_STATUSES[i % len(TIMESHEET_STATUSES)]
            total = Decimal(random.randint(20, 45))
            billable = (total * Decimal('0.7')).quantize(Decimal('0.01'))
            overtime = Decimal(random.randint(0, 6))
            obj = Timesheet.objects.create(
                tenant=tenant,
                number=number,
                owner=random.choice(members) if members else None,
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                period_start=period_start,
                period_end=period_end,
                status=status,
                total_hours=total,
                billable_hours=billable,
                overtime_hours=overtime,
                notes=fake.sentence(nb_words=10),
                submitted_at=(timezone.now() - timedelta(days=random.randint(1, 30))
                              if status in ('submitted', 'approved', 'rejected') else None),
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------------ lines
    def _seed_lines(self, tenant, timesheets, projects):
        created = []
        if not timesheets:
            return created
        for i in range(16):
            timesheet = random.choice(timesheets)
            work_date = timesheet.period_start + timedelta(days=random.randint(0, 6))
            obj = TimesheetLine.objects.create(
                tenant=tenant,
                timesheet=timesheet,
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                work_date=work_date,
                hours=Decimal(random.randint(1, 8)),
                activity=ACTIVITIES[i % len(ACTIVITIES)],
                is_billable=random.random() > 0.25,
                description=fake.sentence(nb_words=6)[:200],
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- approvals
    def _seed_approvals(self, tenant, timesheets, members):
        created = []
        if not timesheets:
            return created
        for i in range(8):
            decision = DECISIONS[i % len(DECISIONS)]
            obj = TimesheetApproval.objects.create(
                tenant=tenant,
                timesheet=random.choice(timesheets),
                approver=random.choice(members) if members else None,
                decision=decision,
                level=1,
                comments=fake.sentence(nb_words=8),
                decided_at=(timezone.now() - timedelta(days=random.randint(1, 30))
                            if decision in ('approved', 'rejected', 'returned') else None),
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------------ leave
    def _seed_leave(self, tenant, members):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(LeaveRecord, 'LV')
            if LeaveRecord.objects.filter(number=number).exists():
                continue
            start_date = today - timedelta(days=random.randint(0, 60))
            span = random.randint(0, 5)
            end_date = start_date + timedelta(days=span)
            days = Decimal(span + 1)
            obj = LeaveRecord.objects.create(
                tenant=tenant,
                number=number,
                owner=random.choice(members) if members else None,
                leave_type=LEAVE_TYPES[i % len(LEAVE_TYPES)],
                start_date=start_date,
                end_date=end_date,
                days=days,
                status=LEAVE_STATUSES[i % len(LEAVE_STATUSES)],
                reason=fake.sentence(nb_words=6)[:200],
                approved_by=(random.choice(members)
                             if members and i % len(LEAVE_STATUSES) == 1 else None),
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- snapshots
    def _seed_snapshots(self, tenant, members, projects):
        created = []
        for i in range(8):
            capacity = Decimal('160.00')
            billable = Decimal(random.randint(60, 150))
            non_billable = (capacity - billable).quantize(Decimal('0.01'))
            if non_billable < 0:
                non_billable = Decimal('0.00')
            utilization = ((billable / capacity) * 100).quantize(Decimal('0.01'))
            obj = UtilizationSnapshot.objects.create(
                tenant=tenant,
                owner=random.choice(members) if members else None,
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                period=PERIODS[i % len(PERIODS)],
                capacity_hours=capacity,
                billable_hours=billable,
                non_billable_hours=non_billable,
                utilization_pct=utilization,
            )
            created.append(obj)
        return created
