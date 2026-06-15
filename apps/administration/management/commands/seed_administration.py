"""Seed idempotent demo data for the System Administration & Security module.

Creates security policies, compliance items, backup jobs, system health
metrics, and access reviews for the acme and globex tenants. Safe to run
repeatedly: each tenant is guarded by an existence check on SecurityPolicy, and
auto-numbered records use an existence-checked number helper.

Usage:
    python manage.py seed_administration
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant

from apps.administration.models import (
    AccessReview,
    BackupJob,
    ComplianceItem,
    SecurityPolicy,
    SystemHealthMetric,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

POLICY_TYPES = ['password', 'mfa', 'session', 'ip_allowlist', 'data_retention', 'encryption']
ENFORCEMENT_LEVELS = ['advisory', 'enforced', 'strict']
POLICY_STATUSES = ['active', 'draft', 'retired']
FRAMEWORKS = ['soc2', 'iso27001', 'gdpr', 'hipaa', 'pci_dss']
COMPLIANCE_STATUSES = ['not_started', 'in_progress', 'compliant', 'non_compliant']
BACKUP_TYPES = ['full', 'incremental', 'differential', 'snapshot']
SCHEDULES = ['hourly', 'daily', 'weekly', 'monthly']
BACKUP_STATUSES = ['scheduled', 'running', 'completed', 'failed']
DESTINATIONS = ['s3://navpms-backups', 'gs://navpms-backups', 'azure://navpms', '/mnt/nas/backups']
METRIC_CATEGORIES = ['cpu', 'memory', 'storage', 'api_latency', 'uptime', 'queue']
METRIC_UNITS = {'cpu': '%', 'memory': '%', 'storage': 'GB', 'api_latency': 'ms', 'uptime': '%', 'queue': 'msgs'}
METRIC_STATUSES = ['healthy', 'warning', 'critical']
REVIEW_STATUSES = ['scheduled', 'in_progress', 'completed', 'overdue']
REVIEW_SCOPES = ['All Users', 'Admin Accounts', 'Service Accounts', 'External Contractors', 'Privileged Roles']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the System Administration & Security module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if SecurityPolicy.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (administration) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding administration for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))

            security_policies = self._seed_security_policies(tenant)
            compliance_items = self._seed_compliance_items(tenant, members)
            backup_jobs = self._seed_backup_jobs(tenant)
            health_metrics = self._seed_health_metrics(tenant)
            access_reviews = self._seed_access_reviews(tenant, members)

            self.stdout.write(self.style.SUCCESS(
                f'    Security policies: {len(security_policies)}  '
                f'Compliance items: {len(compliance_items)}  '
                f'Backup jobs: {len(backup_jobs)}  '
                f'Health metrics: {len(health_metrics)}  '
                f'Access reviews: {len(access_reviews)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nAdministration seed complete.'))
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

    # ------------------------------------------------------- security policies
    def _seed_security_policies(self, tenant):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(SecurityPolicy, 'SEC')
            if SecurityPolicy.objects.filter(number=number).exists():
                continue
            obj = SecurityPolicy.objects.create(
                tenant=tenant,
                number=number,
                name=f'{fake.bs().title()[:140]} Policy',
                policy_type=POLICY_TYPES[i % len(POLICY_TYPES)],
                description=fake.paragraph(nb_sentences=2),
                enforcement_level=ENFORCEMENT_LEVELS[i % len(ENFORCEMENT_LEVELS)],
                last_reviewed=today - timedelta(days=random.randint(0, 180)),
                status=POLICY_STATUSES[i % len(POLICY_STATUSES)],
            )
            created.append(obj)
        return created

    # -------------------------------------------------------- compliance items
    def _seed_compliance_items(self, tenant, members):
        created = []
        today = timezone.now().date()
        for i in range(9):
            number = self._next_number(ComplianceItem, 'CMP')
            if ComplianceItem.objects.filter(number=number).exists():
                continue
            framework = FRAMEWORKS[i % len(FRAMEWORKS)]
            obj = ComplianceItem.objects.create(
                tenant=tenant,
                number=number,
                framework=framework,
                control_id=fake.bothify(text='CC-#.##').upper(),
                title=fake.sentence(nb_words=6).rstrip('.')[:200],
                owner=random.choice(members) if members else None,
                due_date=today + timedelta(days=random.randint(15, 180)),
                status=COMPLIANCE_STATUSES[i % len(COMPLIANCE_STATUSES)],
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------- backup jobs
    def _seed_backup_jobs(self, tenant):
        created = []
        now = timezone.now()
        for i in range(7):
            number = self._next_number(BackupJob, 'BK')
            if BackupJob.objects.filter(number=number).exists():
                continue
            obj = BackupJob.objects.create(
                tenant=tenant,
                number=number,
                name=f'{fake.word().title()} {BACKUP_TYPES[i % len(BACKUP_TYPES)].title()} Backup',
                backup_type=BACKUP_TYPES[i % len(BACKUP_TYPES)],
                schedule=SCHEDULES[i % len(SCHEDULES)],
                destination=random.choice(DESTINATIONS),
                size_mb=Decimal(str(round(random.uniform(50.0, 50000.0), 2))),
                last_run_at=now - timedelta(hours=random.randint(1, 240)),
                retention_days=random.choice([7, 14, 30, 60, 90, 365]),
                status=BACKUP_STATUSES[i % len(BACKUP_STATUSES)],
            )
            created.append(obj)
        return created

    # ----------------------------------------------------- system health metrics
    def _seed_health_metrics(self, tenant):
        created = []
        now = timezone.now()
        for i in range(10):
            number = self._next_number(SystemHealthMetric, 'HM')
            if SystemHealthMetric.objects.filter(number=number).exists():
                continue
            category = METRIC_CATEGORIES[i % len(METRIC_CATEGORIES)]
            obj = SystemHealthMetric.objects.create(
                tenant=tenant,
                number=number,
                metric_name=f'{category.replace("_", " ").title()} {fake.word().title()}',
                category=category,
                value=Decimal(str(round(random.uniform(1.0, 95.0), 2))),
                unit=METRIC_UNITS.get(category, ''),
                threshold=Decimal(str(round(random.uniform(80.0, 100.0), 2))),
                recorded_at=now - timedelta(minutes=random.randint(0, 1440)),
                status=METRIC_STATUSES[i % len(METRIC_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------------- access reviews
    def _seed_access_reviews(self, tenant, members):
        created = []
        today = timezone.now().date()
        for i in range(6):
            number = self._next_number(AccessReview, 'AR')
            if AccessReview.objects.filter(number=number).exists():
                continue
            status = REVIEW_STATUSES[i % len(REVIEW_STATUSES)]
            due_date = today + timedelta(days=random.randint(-30, 90))
            obj = AccessReview.objects.create(
                tenant=tenant,
                number=number,
                title=f'{random.choice(REVIEW_SCOPES)} Access Review {fake.year()}',
                reviewer=random.choice(members) if members else None,
                scope=random.choice(REVIEW_SCOPES),
                users_reviewed=random.randint(0, 250),
                findings=fake.paragraph(nb_sentences=2) if status == 'completed' else '',
                due_date=due_date,
                completed_date=(due_date if status == 'completed' else None),
                status=status,
            )
            created.append(obj)
        return created
