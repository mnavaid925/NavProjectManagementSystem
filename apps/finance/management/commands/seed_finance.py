"""Seed idempotent demo data for the Financial & Billing Management module.

Creates cost centers, invoices, payments, budget-vs-actual records, and
currency rates for the acme and globex tenants. Safe to run repeatedly: each
tenant is guarded by an existence check on CostCenter, and auto-numbered
records use an existence-checked number helper.

Usage:
    python manage.py seed_finance
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

from apps.finance.models import (
    BudgetActual,
    CostCenter,
    CurrencyRate,
    FinanceInvoice,
    Payment,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

COST_CENTER_TYPES = ['department', 'project', 'overhead', 'capital']
COST_CENTER_STATUSES = ['active', 'inactive']
INVOICE_STATUSES = ['draft', 'issued', 'sent', 'paid', 'overdue', 'void']
PAYMENT_METHODS = ['bank_transfer', 'credit_card', 'check', 'cash', 'other']
PAYMENT_STATUSES = ['pending', 'cleared', 'failed', 'refunded']
BUDGET_CATEGORIES = ['labor', 'materials', 'overhead', 'travel', 'other']
BUDGET_STATUSES = ['open', 'closed']
RATE_STATUSES = ['active', 'retired']
PERIODS = ['2025-Q4', '2026-Q1', '2026-Q2', '2026-Q3']
CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY']
TARGET_CURRENCIES = ['EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'INR']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Financial & Billing Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if CostCenter.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (finance) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding finance for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            cost_centers = self._seed_cost_centers(tenant, members)
            invoices = self._seed_invoices(tenant, projects, cost_centers)
            payments = self._seed_payments(tenant, invoices)
            budget_actuals = self._seed_budget_actuals(tenant, projects, cost_centers)
            currency_rates = self._seed_currency_rates(tenant)

            self.stdout.write(self.style.SUCCESS(
                f'    Cost centers: {len(cost_centers)}  Invoices: {len(invoices)}  '
                f'Payments: {len(payments)}  Budget actuals: {len(budget_actuals)}  '
                f'Currency rates: {len(currency_rates)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nFinance seed complete.'))
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

    # ----------------------------------------------------------- cost centers
    def _seed_cost_centers(self, tenant, members):
        created = []
        for i in range(10):
            number = self._next_number(CostCenter, 'CC')
            if CostCenter.objects.filter(number=number).exists():
                continue
            budget = Decimal(random.randint(20000, 500000))
            actual = (budget * Decimal(str(round(random.uniform(0.3, 1.1), 2)))).quantize(Decimal('0.01'))
            obj = CostCenter.objects.create(
                tenant=tenant,
                number=number,
                name=fake.bs().title()[:160],
                code=f'CC{random.randint(100, 999)}',
                manager=random.choice(members) if members else None,
                cost_center_type=COST_CENTER_TYPES[i % len(COST_CENTER_TYPES)],
                budget=budget,
                actual_cost=actual,
                status=COST_CENTER_STATUSES[i % len(COST_CENTER_STATUSES)],
                description=fake.paragraph(nb_sentences=2),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- invoices
    def _seed_invoices(self, tenant, projects, cost_centers):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(FinanceInvoice, 'FINV')
            if FinanceInvoice.objects.filter(number=number).exists():
                continue
            status = INVOICE_STATUSES[i % len(INVOICE_STATUSES)]
            amount = Decimal(random.randint(1000, 80000))
            tax = (amount * Decimal('0.10')).quantize(Decimal('0.01'))
            issue_date = today - timedelta(days=random.randint(0, 120))
            due_date = issue_date + timedelta(days=30)
            obj = FinanceInvoice.objects.create(
                tenant=tenant,
                number=number,
                client_name=fake.company()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                cost_center=(random.choice(cost_centers)
                             if cost_centers and random.random() > 0.3 else None),
                amount=amount,
                tax_amount=tax,
                currency=random.choice(['USD', 'EUR', 'GBP']),
                status=status,
                issue_date=issue_date,
                due_date=due_date,
                paid_date=(issue_date + timedelta(days=random.randint(1, 40))
                           if status == 'paid' else None),
                notes=fake.sentence(nb_words=10),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- payments
    def _seed_payments(self, tenant, invoices):
        created = []
        today = timezone.now().date()
        for i in range(7):
            number = self._next_number(Payment, 'PAY')
            if Payment.objects.filter(number=number).exists():
                continue
            invoice = (random.choice(invoices)
                       if invoices and random.random() > 0.2 else None)
            obj = Payment.objects.create(
                tenant=tenant,
                number=number,
                invoice=invoice,
                amount=(invoice.amount if invoice else Decimal(random.randint(500, 50000))),
                currency=(invoice.currency if invoice else 'USD'),
                method=PAYMENT_METHODS[i % len(PAYMENT_METHODS)],
                status=PAYMENT_STATUSES[i % len(PAYMENT_STATUSES)],
                payment_date=today - timedelta(days=random.randint(0, 90)),
                reference=fake.bothify(text='REF-####-????').upper(),
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------- budget actual
    def _seed_budget_actuals(self, tenant, projects, cost_centers):
        created = []
        for i in range(8):
            number = self._next_number(BudgetActual, 'BA')
            if BudgetActual.objects.filter(number=number).exists():
                continue
            budget = Decimal(random.randint(10000, 200000))
            actual = (budget * Decimal(str(round(random.uniform(0.4, 1.2), 2)))).quantize(Decimal('0.01'))
            obj = BudgetActual.objects.create(
                tenant=tenant,
                number=number,
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                cost_center=(random.choice(cost_centers)
                             if cost_centers and random.random() > 0.3 else None),
                period=random.choice(PERIODS),
                category=BUDGET_CATEGORIES[i % len(BUDGET_CATEGORIES)],
                budget_amount=budget,
                actual_amount=actual,
                status=BUDGET_STATUSES[i % len(BUDGET_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------------- currency rates
    def _seed_currency_rates(self, tenant):
        created = []
        today = timezone.now().date()
        for i in range(6):
            target = TARGET_CURRENCIES[i % len(TARGET_CURRENCIES)]
            obj = CurrencyRate.objects.create(
                tenant=tenant,
                base_currency='USD',
                target_currency=target,
                rate=Decimal(str(round(random.uniform(0.5, 150.0), 6))),
                effective_date=today - timedelta(days=random.randint(0, 60)),
                source=random.choice(['ECB', 'OpenExchangeRates', 'XE', 'Manual entry']),
                status=RATE_STATUSES[i % len(RATE_STATUSES)],
            )
            created.append(obj)
        return created
