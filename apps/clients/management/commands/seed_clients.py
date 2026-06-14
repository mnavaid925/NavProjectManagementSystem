"""Seed idempotent demo data for the Client & External Collaboration module.

Creates client access records, client feedback, SOW contracts, external
vendors, and client invoices for the acme and globex tenants. Safe to run
repeatedly: each tenant is guarded by an existence check on ClientAccess, and
auto-numbered records use an existence-checked number helper.

Usage:
    python manage.py seed_clients
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

from apps.clients.models import (
    ClientAccess,
    ClientFeedback,
    ClientInvoice,
    ExternalVendor,
    SOWContract,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

ACCESS_LEVELS = ['view_only', 'comment', 'approve']
ACCESS_STATUSES = ['active', 'suspended', 'revoked']
FEEDBACK_TYPES = ['praise', 'concern', 'request', 'approval']
FEEDBACK_STATUSES = ['new', 'in_review', 'addressed', 'closed']
CONTRACT_TYPES = ['fixed_fee', 'time_materials', 'retainer', 'milestone']
CONTRACT_STATUSES = ['draft', 'sent', 'signed', 'active', 'expired', 'terminated']
SERVICE_TYPES = ['consulting', 'development', 'design', 'infrastructure', 'other']
VENDOR_STATUSES = ['active', 'inactive', 'blacklisted']
BILLING_TYPES = ['time_materials', 'fixed_fee', 'milestone']
INVOICE_STATUSES = ['draft', 'sent', 'paid', 'partially_paid', 'overdue']
CURRENCIES = ['USD', 'EUR', 'GBP']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Client & External Collaboration module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if ClientAccess.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (clients) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding clients for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))  # noqa: F841 (parity w/ scope)
            projects = list(Project.objects.filter(tenant=tenant))

            access_records = self._seed_access(tenant, projects)
            feedback_items = self._seed_feedback(tenant, projects)
            contracts = self._seed_contracts(tenant, projects)
            vendors = self._seed_vendors(tenant)
            invoices = self._seed_invoices(tenant, projects, contracts)

            self.stdout.write(self.style.SUCCESS(
                f'    Access: {len(access_records)}  Feedback: {len(feedback_items)}  '
                f'Contracts: {len(contracts)}  Vendors: {len(vendors)}  '
                f'Invoices: {len(invoices)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nClients seed complete.'))
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

    # --------------------------------------------------------- access records
    def _seed_access(self, tenant, projects):
        created = []
        for i in range(10):
            number = self._next_number(ClientAccess, 'CA')
            if ClientAccess.objects.filter(number=number).exists():
                continue
            obj = ClientAccess.objects.create(
                tenant=tenant,
                number=number,
                client_name=fake.company()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                contact_name=fake.name()[:120],
                contact_email=fake.company_email(),
                access_level=ACCESS_LEVELS[i % len(ACCESS_LEVELS)],
                portal_enabled=random.random() > 0.2,
                status=ACCESS_STATUSES[i % len(ACCESS_STATUSES)],
                notes=fake.sentence(nb_words=10),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- feedback
    def _seed_feedback(self, tenant, projects):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(ClientFeedback, 'CF')
            if ClientFeedback.objects.filter(number=number).exists():
                continue
            obj = ClientFeedback.objects.create(
                tenant=tenant,
                number=number,
                client_name=fake.company()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                subject=fake.catch_phrase()[:160],
                feedback_type=FEEDBACK_TYPES[i % len(FEEDBACK_TYPES)],
                rating=random.randint(1, 5),
                status=FEEDBACK_STATUSES[i % len(FEEDBACK_STATUSES)],
                submitted_date=today - timedelta(days=random.randint(0, 90)),
                details=fake.paragraph(nb_sentences=2),
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- contracts
    def _seed_contracts(self, tenant, projects):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(SOWContract, 'SOW')
            if SOWContract.objects.filter(number=number).exists():
                continue
            status = CONTRACT_STATUSES[i % len(CONTRACT_STATUSES)]
            start = today - timedelta(days=random.randint(30, 300))
            obj = SOWContract.objects.create(
                tenant=tenant,
                number=number,
                title=fake.bs().title()[:160],
                client_name=fake.company()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                contract_type=CONTRACT_TYPES[i % len(CONTRACT_TYPES)],
                value=Decimal(random.randint(5000, 500000)),
                currency=random.choice(CURRENCIES),
                start_date=start,
                end_date=start + timedelta(days=random.randint(60, 365)),
                status=status,
                signed_date=(start + timedelta(days=random.randint(1, 20))
                             if status in ('signed', 'active', 'expired', 'terminated') else None),
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------------- vendors
    def _seed_vendors(self, tenant):
        created = []
        for i in range(7):
            number = self._next_number(ExternalVendor, 'VEN')
            if ExternalVendor.objects.filter(number=number).exists():
                continue
            obj = ExternalVendor.objects.create(
                tenant=tenant,
                number=number,
                name=fake.company()[:160],
                contact_name=fake.name()[:120],
                contact_email=fake.company_email(),
                service_type=SERVICE_TYPES[i % len(SERVICE_TYPES)],
                status=VENDOR_STATUSES[i % len(VENDOR_STATUSES)],
                rating=random.randint(1, 5),
                notes=fake.sentence(nb_words=10),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- invoices
    def _seed_invoices(self, tenant, projects, contracts):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(ClientInvoice, 'CINV')
            if ClientInvoice.objects.filter(number=number).exists():
                continue
            status = INVOICE_STATUSES[i % len(INVOICE_STATUSES)]
            issue = today - timedelta(days=random.randint(0, 120))
            obj = ClientInvoice.objects.create(
                tenant=tenant,
                number=number,
                client_name=fake.company()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                contract=(random.choice(contracts)
                          if contracts and random.random() > 0.4 else None),
                amount=Decimal(random.randint(1000, 100000)),
                currency=random.choice(CURRENCIES),
                billing_type=BILLING_TYPES[i % len(BILLING_TYPES)],
                status=status,
                issue_date=issue,
                due_date=issue + timedelta(days=30),
                paid_date=(issue + timedelta(days=random.randint(5, 40))
                           if status == 'paid' else None),
            )
            created.append(obj)
        return created
