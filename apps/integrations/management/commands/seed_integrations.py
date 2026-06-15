"""Seed idempotent demo data for the Integration & API Hub module.

Creates connectors, sync jobs, sync logs, webhooks, and API keys for the acme
and globex tenants. Safe to run repeatedly: each tenant is guarded by an
existence check on Connector, and auto-numbered records use an
existence-checked number helper.

Security note: webhook secrets are demo placeholder tokens, and API keys store
only a short displayable prefix plus a sha256 hash of a throwaway random secret
- the raw key is never persisted.

Usage:
    python manage.py seed_integrations
"""
import hashlib
import random
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.integrations.models import (
    ApiKey,
    Connector,
    SyncJob,
    SyncLog,
    Webhook,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

CONNECTOR_CATEGORIES = ['erp', 'crm', 'hr', 'devops', 'storage']
CONNECTOR_AUTH_TYPES = ['oauth2', 'api_key', 'basic', 'token']
CONNECTOR_STATUSES = ['connected', 'disconnected', 'error', 'pending']
PROVIDERS = ['Salesforce', 'SAP', 'Workday', 'GitHub', 'Dropbox', 'NetSuite',
             'HubSpot', 'Bamboo HR', 'GitLab', 'Google Drive']
JOB_DIRECTIONS = ['inbound', 'outbound', 'bidirectional']
JOB_SCHEDULES = ['manual', 'hourly', 'daily', 'weekly']
JOB_STATUSES = ['idle', 'running', 'completed', 'failed']
LOG_LEVELS = ['info', 'warning', 'error']
LOG_STATUSES = ['success', 'partial', 'failed']
WEBHOOK_STATUSES = ['active', 'inactive', 'failed']
WEBHOOK_EVENTS = ['record.created', 'record.updated', 'record.deleted',
                  'sync.completed', 'sync.failed', 'invoice.paid']
APIKEY_STATUSES = ['active', 'revoked', 'expired']
SCOPES = ['read', 'read,write', 'read,write,delete', 'admin', 'webhooks:manage']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Integration & API Hub module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Connector.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (integrations) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding integrations for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))  # noqa: F841 (parity)

            connectors = self._seed_connectors(tenant, members)
            sync_jobs = self._seed_sync_jobs(tenant, connectors)
            sync_logs = self._seed_sync_logs(tenant, connectors, sync_jobs)
            webhooks = self._seed_webhooks(tenant)
            api_keys = self._seed_api_keys(tenant, members)

            self.stdout.write(self.style.SUCCESS(
                f'    Connectors: {len(connectors)}  Sync jobs: {len(sync_jobs)}  '
                f'Sync logs: {len(sync_logs)}  Webhooks: {len(webhooks)}  '
                f'API keys: {len(api_keys)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nIntegrations seed complete.'))
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

    # ------------------------------------------------------------- connectors
    def _seed_connectors(self, tenant, members):
        created = []
        now = timezone.now()
        for i in range(10):
            number = self._next_number(Connector, 'CON')
            if Connector.objects.filter(number=number).exists():
                continue
            status = CONNECTOR_STATUSES[i % len(CONNECTOR_STATUSES)]
            obj = Connector.objects.create(
                tenant=tenant,
                number=number,
                name=f'{random.choice(PROVIDERS)} Connector',
                category=CONNECTOR_CATEGORIES[i % len(CONNECTOR_CATEGORIES)],
                provider=random.choice(PROVIDERS),
                auth_type=CONNECTOR_AUTH_TYPES[i % len(CONNECTOR_AUTH_TYPES)],
                base_url=fake.url(),
                owner=random.choice(members) if members else None,
                last_sync_at=(now - timedelta(hours=random.randint(1, 240))
                              if status == 'connected' else None),
                status=status,
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- sync jobs
    def _seed_sync_jobs(self, tenant, connectors):
        created = []
        now = timezone.now()
        for i in range(8):
            number = self._next_number(SyncJob, 'SJ')
            if SyncJob.objects.filter(number=number).exists():
                continue
            obj = SyncJob.objects.create(
                tenant=tenant,
                number=number,
                name=f'{fake.word().title()} Sync',
                connector=(random.choice(connectors)
                           if connectors and random.random() > 0.2 else None),
                direction=JOB_DIRECTIONS[i % len(JOB_DIRECTIONS)],
                schedule=JOB_SCHEDULES[i % len(JOB_SCHEDULES)],
                records_synced=random.randint(0, 50000),
                last_run_at=now - timedelta(hours=random.randint(1, 168)),
                next_run_at=now + timedelta(hours=random.randint(1, 168)),
                status=JOB_STATUSES[i % len(JOB_STATUSES)],
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- sync logs
    def _seed_sync_logs(self, tenant, connectors, sync_jobs):
        created = []
        now = timezone.now()
        for i in range(10):
            number = self._next_number(SyncLog, 'SL')
            if SyncLog.objects.filter(number=number).exists():
                continue
            obj = SyncLog.objects.create(
                tenant=tenant,
                number=number,
                connector=(random.choice(connectors)
                           if connectors and random.random() > 0.2 else None),
                sync_job=(random.choice(sync_jobs)
                          if sync_jobs and random.random() > 0.3 else None),
                level=LOG_LEVELS[i % len(LOG_LEVELS)],
                message=fake.sentence(nb_words=10),
                records_processed=random.randint(0, 20000),
                logged_at=now - timedelta(hours=random.randint(0, 240)),
                status=LOG_STATUSES[i % len(LOG_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- webhooks
    def _seed_webhooks(self, tenant):
        created = []
        now = timezone.now()
        for i in range(7):
            number = self._next_number(Webhook, 'WH')
            if Webhook.objects.filter(number=number).exists():
                continue
            status = WEBHOOK_STATUSES[i % len(WEBHOOK_STATUSES)]
            obj = Webhook.objects.create(
                tenant=tenant,
                number=number,
                name=f'{fake.word().title()} Webhook',
                target_url=fake.url(),
                event=random.choice(WEBHOOK_EVENTS),
                # Demo placeholder only - never store a real secret in seed data.
                secret='whsec_demo_placeholder',
                last_triggered_at=(now - timedelta(hours=random.randint(1, 200))
                                   if status == 'active' else None),
                status=status,
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- api keys
    def _seed_api_keys(self, tenant, members):
        created = []
        now = timezone.now()
        today = now.date()
        for i in range(8):
            number = self._next_number(ApiKey, 'AK')
            if ApiKey.objects.filter(number=number).exists():
                continue
            # Never persist the raw key: generate a throwaway secret, keep only a
            # short displayable prefix and a one-way sha256 hash.
            raw_secret = secrets.token_hex(24)
            key_prefix = 'navpms_' + fake.lexify(text='????????').lower()
            hashed_key = hashlib.sha256(raw_secret.encode('utf-8')).hexdigest()
            status = APIKEY_STATUSES[i % len(APIKEY_STATUSES)]
            obj = ApiKey.objects.create(
                tenant=tenant,
                number=number,
                name=f'{fake.word().title()} API Key',
                key_prefix=key_prefix,
                hashed_key=hashed_key,
                scopes=random.choice(SCOPES),
                owner=random.choice(members) if members else None,
                expires_at=today + timedelta(days=random.randint(30, 365)),
                last_used_at=(now - timedelta(hours=random.randint(1, 300))
                              if status == 'active' else None),
                status=status,
            )
            created.append(obj)
        return created
