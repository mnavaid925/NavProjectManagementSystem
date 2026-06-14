"""Seed idempotent demo data for the Portfolio & Program Management module.

Creates portfolios, programs, program dependencies, strategic goals, and
capacity plans for the acme and globex tenants. Safe to run repeatedly: each
tenant is guarded by an existence check on Portfolio, and auto-numbered records
use an existence-checked number helper.

Usage:
    python manage.py seed_portfolio
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant

from apps.portfolio.models import (
    CapacityPlan,
    Portfolio,
    Program,
    ProgramDependency,
    StrategicGoal,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

PORTFOLIO_STATUSES = ['active', 'on_hold', 'closed']
HEALTHS = ['green', 'amber', 'red']
PORTFOLIO_PRIORITIES = ['low', 'medium', 'high', 'critical']
PROGRAM_STATUSES = ['planning', 'active', 'on_hold', 'completed', 'cancelled']
DEPENDENCY_TYPES = ['finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish']
DEPENDENCY_STATUSES = ['open', 'in_progress', 'resolved', 'blocked']
GOAL_CATEGORIES = ['growth', 'efficiency', 'innovation', 'compliance', 'customer']
GOAL_PRIORITIES = ['low', 'medium', 'high', 'critical']
GOAL_STATUSES = ['proposed', 'active', 'achieved', 'missed']
CAPACITY_STATUSES = ['draft', 'published']
PERIODS = ['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026', 'H1 2026', 'H2 2026']
TEAMS = ['Platform', 'Mobile', 'Data', 'Infrastructure', 'Design', 'QA', 'Security']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Portfolio & Program Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Portfolio.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (portfolio) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding portfolio for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))

            portfolios = self._seed_portfolios(tenant, members)
            programs = self._seed_programs(tenant, members, portfolios)
            dependencies = self._seed_dependencies(tenant, programs)
            goals = self._seed_goals(tenant, portfolios)
            capacity_plans = self._seed_capacity_plans(tenant, portfolios)

            self.stdout.write(self.style.SUCCESS(
                f'    Portfolios: {len(portfolios)}  Programs: {len(programs)}  '
                f'Dependencies: {len(dependencies)}  Goals: {len(goals)}  '
                f'Capacity plans: {len(capacity_plans)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nPortfolio seed complete.'))
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

    # ------------------------------------------------------------ portfolios
    def _seed_portfolios(self, tenant, members):
        created = []
        for i in range(9):
            number = self._next_number(Portfolio, 'PF')
            if Portfolio.objects.filter(number=number).exists():
                continue
            obj = Portfolio.objects.create(
                tenant=tenant,
                number=number,
                name=fake.catch_phrase()[:160],
                description=fake.paragraph(nb_sentences=3),
                portfolio_manager=random.choice(members) if members else None,
                status=PORTFOLIO_STATUSES[i % len(PORTFOLIO_STATUSES)],
                health=HEALTHS[i % len(HEALTHS)],
                strategic_priority=PORTFOLIO_PRIORITIES[i % len(PORTFOLIO_PRIORITIES)],
                total_budget=random.randint(100000, 5000000),
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- programs
    def _seed_programs(self, tenant, members, portfolios):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(Program, 'PRG')
            if Program.objects.filter(number=number).exists():
                continue
            start = today - timedelta(days=random.randint(0, 180))
            obj = Program.objects.create(
                tenant=tenant,
                number=number,
                portfolio=(random.choice(portfolios)
                           if portfolios and random.random() > 0.2 else None),
                name=fake.catch_phrase()[:160],
                description=fake.paragraph(nb_sentences=3),
                program_manager=random.choice(members) if members else None,
                status=PROGRAM_STATUSES[i % len(PROGRAM_STATUSES)],
                health=HEALTHS[i % len(HEALTHS)],
                start_date=start,
                end_date=start + timedelta(days=random.randint(90, 360)),
                budget=random.randint(50000, 2000000),
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------- dependencies
    def _seed_dependencies(self, tenant, programs):
        created = []
        if len(programs) < 2:
            return created
        for i in range(7):
            program = random.choice(programs)
            depends_on = random.choice([p for p in programs if p.pk != program.pk])
            obj = ProgramDependency.objects.create(
                tenant=tenant,
                program=program,
                depends_on=depends_on if random.random() > 0.2 else None,
                dependency_type=DEPENDENCY_TYPES[i % len(DEPENDENCY_TYPES)],
                status=DEPENDENCY_STATUSES[i % len(DEPENDENCY_STATUSES)],
                lag_days=random.randint(0, 30),
                description=fake.paragraph(nb_sentences=2),
            )
            created.append(obj)
        return created

    # ----------------------------------------------------------------- goals
    def _seed_goals(self, tenant, portfolios):
        created = []
        today = timezone.now().date()
        for i in range(7):
            number = self._next_number(StrategicGoal, 'SG')
            if StrategicGoal.objects.filter(number=number).exists():
                continue
            obj = StrategicGoal.objects.create(
                tenant=tenant,
                number=number,
                title=fake.bs().title()[:160],
                description=fake.paragraph(nb_sentences=3),
                portfolio=(random.choice(portfolios)
                           if portfolios and random.random() > 0.3 else None),
                category=GOAL_CATEGORIES[i % len(GOAL_CATEGORIES)],
                alignment_score=random.randint(0, 100),
                priority=GOAL_PRIORITIES[i % len(GOAL_PRIORITIES)],
                target_date=today + timedelta(days=random.randint(30, 365)),
                status=GOAL_STATUSES[i % len(GOAL_STATUSES)],
            )
            created.append(obj)
        return created

    # -------------------------------------------------------- capacity plans
    def _seed_capacity_plans(self, tenant, portfolios):
        created = []
        for i in range(6):
            number = self._next_number(CapacityPlan, 'CP')
            if CapacityPlan.objects.filter(number=number).exists():
                continue
            obj = CapacityPlan.objects.create(
                tenant=tenant,
                number=number,
                portfolio=(random.choice(portfolios)
                           if portfolios and random.random() > 0.3 else None),
                period=PERIODS[i % len(PERIODS)],
                team=random.choice(TEAMS),
                demand_hours=random.randint(400, 2000),
                capacity_hours=random.randint(400, 2000),
                status=CAPACITY_STATUSES[i % len(CAPACITY_STATUSES)],
                notes=fake.paragraph(nb_sentences=2),
            )
            created.append(obj)
        return created
