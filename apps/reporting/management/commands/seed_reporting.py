"""Seed idempotent demo data for the Reporting & Business Intelligence module.

Creates report definitions, report runs, dashboard widgets, executive packs,
and data exports for the acme and globex tenants. Safe to run repeatedly: each
tenant is guarded by an existence check on ReportDefinition, and auto-numbered
records use an existence-checked number helper.

Usage:
    python manage.py seed_reporting
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.reporting.models import (
    DashboardWidget,
    DataExport,
    ExecutivePack,
    ReportDefinition,
    ReportRun,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

REPORT_CATEGORIES = ['status', 'risk', 'financial', 'resource', 'schedule', 'custom']
DATA_SOURCES = ['projects', 'tasks', 'risks', 'finance', 'resources', 'timesheets']
VISIBILITIES = ['private', 'team', 'tenant']
REPORT_STATUSES = ['draft', 'active', 'archived']
RUN_FORMATS = ['html', 'pdf', 'csv', 'xlsx']
RUN_STATUSES = ['queued', 'running', 'completed', 'failed']
WIDGET_TYPES = ['kpi_card', 'line_chart', 'bar_chart', 'pie_chart', 'table', 'gauge']
WIDGET_STATUSES = ['active', 'hidden']
RAG_STATUSES = ['red', 'amber', 'green']
PACK_STATUSES = ['draft', 'published', 'archived']
EXPORT_TYPES = ['csv', 'excel', 'pdf', 'json', 'odata', 'rest_api']
EXPORT_STATUSES = ['pending', 'running', 'completed', 'failed']
PERIODS = ['2025-Q4', '2026-Q1', '2026-Q2', '2026-Q3']
METRICS = ['Active Projects', 'Open Risks', 'Budget Variance', 'Utilization %',
           'Tasks Completed', 'Overdue Invoices', 'Logged Hours', 'Burn Rate']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Reporting & Business Intelligence module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if ReportDefinition.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (reporting) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding reporting for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            definitions = self._seed_definitions(tenant, projects, members)
            runs = self._seed_runs(tenant, definitions, members)
            widgets = self._seed_widgets(tenant, members)
            packs = self._seed_packs(tenant, projects, members)
            exports = self._seed_exports(tenant, members)

            self.stdout.write(self.style.SUCCESS(
                f'    Report definitions: {len(definitions)}  Report runs: {len(runs)}  '
                f'Widgets: {len(widgets)}  Executive packs: {len(packs)}  '
                f'Data exports: {len(exports)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nReporting seed complete.'))
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

    # ----------------------------------------------------- report definitions
    def _seed_definitions(self, tenant, projects, members):
        created = []
        for i in range(8):
            number = self._next_number(ReportDefinition, 'RPT')
            if ReportDefinition.objects.filter(number=number).exists():
                continue
            obj = ReportDefinition.objects.create(
                tenant=tenant,
                number=number,
                name=fake.catch_phrase()[:160],
                category=REPORT_CATEGORIES[i % len(REPORT_CATEGORIES)],
                data_source=DATA_SOURCES[i % len(DATA_SOURCES)],
                visibility=VISIBILITIES[i % len(VISIBILITIES)],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                owner=random.choice(members) if members else None,
                description=fake.paragraph(nb_sentences=2),
                is_scheduled=random.random() > 0.5,
                status=REPORT_STATUSES[i % len(REPORT_STATUSES)],
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------- report runs
    def _seed_runs(self, tenant, definitions, members):
        created = []
        now = timezone.now()
        for i in range(9):
            number = self._next_number(ReportRun, 'RUN')
            if ReportRun.objects.filter(number=number).exists():
                continue
            obj = ReportRun.objects.create(
                tenant=tenant,
                number=number,
                report=(random.choice(definitions)
                        if definitions and random.random() > 0.2 else None),
                run_by=random.choice(members) if members else None,
                format=RUN_FORMATS[i % len(RUN_FORMATS)],
                row_count=random.randint(0, 5000),
                duration_ms=random.randint(50, 30000),
                started_at=now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23)),
                notes=fake.sentence(nb_words=10),
                status=RUN_STATUSES[i % len(RUN_STATUSES)],
            )
            created.append(obj)
        return created

    # -------------------------------------------------------- dashboard widgets
    def _seed_widgets(self, tenant, members):
        created = []
        for i in range(8):
            number = self._next_number(DashboardWidget, 'WID')
            if DashboardWidget.objects.filter(number=number).exists():
                continue
            obj = DashboardWidget.objects.create(
                tenant=tenant,
                number=number,
                title=random.choice(METRICS),
                widget_type=WIDGET_TYPES[i % len(WIDGET_TYPES)],
                metric=fake.word().title(),
                data_source=DATA_SOURCES[i % len(DATA_SOURCES)],
                position=i,
                refresh_interval=random.choice([30, 60, 120, 300, 600]),
                owner=random.choice(members) if members else None,
                status=WIDGET_STATUSES[i % len(WIDGET_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------------- executive packs
    def _seed_packs(self, tenant, projects, members):
        created = []
        today = timezone.now().date()
        for i in range(7):
            number = self._next_number(ExecutivePack, 'EP')
            if ExecutivePack.objects.filter(number=number).exists():
                continue
            status = PACK_STATUSES[i % len(PACK_STATUSES)]
            obj = ExecutivePack.objects.create(
                tenant=tenant,
                number=number,
                title=f'{random.choice(PERIODS)} Executive Pack'[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                period=random.choice(PERIODS),
                rag_status=RAG_STATUSES[i % len(RAG_STATUSES)],
                summary=fake.paragraph(nb_sentences=3),
                prepared_by=random.choice(members) if members else None,
                published_date=(today - timedelta(days=random.randint(0, 90))
                                if status == 'published' else None),
                status=status,
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------- data exports
    def _seed_exports(self, tenant, members):
        created = []
        now = timezone.now()
        for i in range(8):
            number = self._next_number(DataExport, 'EXP')
            if DataExport.objects.filter(number=number).exists():
                continue
            status = EXPORT_STATUSES[i % len(EXPORT_STATUSES)]
            export_type = EXPORT_TYPES[i % len(EXPORT_TYPES)]
            obj = DataExport.objects.create(
                tenant=tenant,
                number=number,
                name=f'{fake.word().title()} {export_type.upper()} Export'[:160],
                export_type=export_type,
                destination=fake.uri()[:200],
                data_source=DATA_SOURCES[i % len(DATA_SOURCES)],
                record_count=random.randint(0, 100000),
                requested_by=random.choice(members) if members else None,
                completed_at=(now - timedelta(days=random.randint(0, 45))
                              if status == 'completed' else None),
                status=status,
            )
            created.append(obj)
        return created
