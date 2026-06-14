"""Seed idempotent demo data for the Cost & Budget Management module.

Creates budgets, control accounts, expenses, cost forecasts, and budget
changes for the acme and globex tenants. Safe to run repeatedly: each tenant
is guarded by an existence check on Budget, and auto-numbered records use an
existence-checked number helper.

Usage:
    python manage.py seed_budgeting
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

from apps.budgeting.models import (
    Budget,
    BudgetChange,
    ControlAccount,
    CostForecast,
    Expense,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

BUDGET_CATEGORIES = ['labor', 'material', 'overhead', 'contingency', 'equipment']
BUDGET_STATUSES = ['draft', 'approved', 'active', 'closed']
CA_STATUSES = ['open', 'in_progress', 'closed']
EXPENSE_CATEGORIES = ['labor', 'material', 'travel', 'equipment', 'other']
EXPENSE_TYPES = ['commitment', 'actual']
EXPENSE_STATUSES = ['draft', 'submitted', 'approved', 'rejected', 'paid']
FORECAST_METHODS = ['cpi_based', 'manual', 'spi_cpi']
FORECAST_STATUSES = ['draft', 'published']
CHANGE_TYPES = ['increase', 'decrease', 'reallocation']
CHANGE_STATUSES = ['pending', 'approved', 'rejected', 'implemented']
CURRENCIES = ['USD', 'EUR', 'GBP']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Cost & Budget Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Budget.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (budgeting) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding budgeting for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            budgets = self._seed_budgets(tenant, members, projects)
            control_accounts = self._seed_control_accounts(tenant, members, projects, budgets)
            expenses = self._seed_expenses(tenant, members, projects, control_accounts)
            forecasts = self._seed_forecasts(tenant, projects, budgets)
            changes = self._seed_changes(tenant, members, budgets)

            self.stdout.write(self.style.SUCCESS(
                f'    Budgets: {len(budgets)}  Control accounts: {len(control_accounts)}  '
                f'Expenses: {len(expenses)}  Forecasts: {len(forecasts)}  '
                f'Changes: {len(changes)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nBudgeting seed complete.'))
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

    # ---------------------------------------------------------------- budgets
    def _seed_budgets(self, tenant, members, projects):
        created = []
        for i in range(6):
            number = self._next_number(Budget, 'BUD')
            if Budget.objects.filter(number=number).exists():
                continue
            planned = Decimal(random.randint(50, 800) * 1000)
            allocated = (planned * Decimal(str(round(random.uniform(0.2, 0.95), 2)))).quantize(Decimal('0.01'))
            obj = Budget.objects.create(
                tenant=tenant,
                number=number,
                name=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                fiscal_year=str(random.choice([2025, 2026, 2027])),
                category=random.choice(BUDGET_CATEGORIES),
                planned_amount=planned,
                allocated_amount=allocated,
                currency=random.choice(CURRENCIES),
                owner=random.choice(members) if members else None,
                status=BUDGET_STATUSES[i % len(BUDGET_STATUSES)],
                notes=fake.sentence(nb_words=10),
            )
            created.append(obj)
        return created

    # -------------------------------------------------------- control accounts
    def _seed_control_accounts(self, tenant, members, projects, budgets):
        created = []
        for i in range(6):
            bac = Decimal(random.randint(40, 600) * 1000)
            ev = (bac * Decimal(str(round(random.uniform(0.1, 0.9), 2)))).quantize(Decimal('0.01'))
            ac = (ev * Decimal(str(round(random.uniform(0.8, 1.3), 2)))).quantize(Decimal('0.01'))
            obj = ControlAccount.objects.create(
                tenant=tenant,
                code=f'CA-{i + 1:03d}',
                name=fake.bs().title()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                budget=random.choice(budgets) if budgets and random.random() > 0.2 else None,
                manager=random.choice(members) if members else None,
                bac=bac,
                earned_value=ev,
                actual_cost=ac,
                status=CA_STATUSES[i % len(CA_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- expenses
    def _seed_expenses(self, tenant, members, projects, control_accounts):
        created = []
        today = timezone.now().date()
        for i in range(12):
            number = self._next_number(Expense, 'EXP')
            if Expense.objects.filter(number=number).exists():
                continue
            obj = Expense.objects.create(
                tenant=tenant,
                number=number,
                description=fake.sentence(nb_words=6)[:200],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                control_account=random.choice(control_accounts) if control_accounts and random.random() > 0.3 else None,
                category=random.choice(EXPENSE_CATEGORIES),
                amount=Decimal(random.randint(5, 250) * 100),
                expense_date=today - timedelta(days=random.randint(0, 120)),
                vendor=fake.company()[:160],
                expense_type=random.choice(EXPENSE_TYPES),
                status=EXPENSE_STATUSES[i % len(EXPENSE_STATUSES)],
                submitted_by=random.choice(members) if members else None,
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- forecasts
    def _seed_forecasts(self, tenant, projects, budgets):
        created = []
        for i in range(6):
            bac = Decimal(random.randint(50, 700) * 1000)
            eac = (bac * Decimal(str(round(random.uniform(0.85, 1.25), 2)))).quantize(Decimal('0.01'))
            etc = (eac * Decimal(str(round(random.uniform(0.2, 0.7), 2)))).quantize(Decimal('0.01'))
            obj = CostForecast.objects.create(
                tenant=tenant,
                name=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                budget=random.choice(budgets) if budgets and random.random() > 0.2 else None,
                period=f'2026-{(i % 12) + 1:02d}',
                bac=bac,
                eac=eac,
                etc=etc,
                method=random.choice(FORECAST_METHODS),
                status=FORECAST_STATUSES[i % len(FORECAST_STATUSES)],
                notes=fake.sentence(nb_words=8)[:200],
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------------- changes
    def _seed_changes(self, tenant, members, budgets):
        created = []
        today = timezone.now().date()
        for i in range(6):
            number = self._next_number(BudgetChange, 'BCR')
            if BudgetChange.objects.filter(number=number).exists():
                continue
            status = CHANGE_STATUSES[i % len(CHANGE_STATUSES)]
            obj = BudgetChange.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                budget=random.choice(budgets) if budgets and random.random() > 0.2 else None,
                change_type=random.choice(CHANGE_TYPES),
                amount=Decimal(random.randint(5, 200) * 1000),
                reason=fake.paragraph(nb_sentences=2),
                status=status,
                requested_by=random.choice(members) if members else None,
                decided_at=today - timedelta(days=random.randint(1, 60)) if status in ('approved', 'rejected', 'implemented') else None,
            )
            created.append(obj)
        return created
