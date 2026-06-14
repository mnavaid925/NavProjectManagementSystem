"""Seed idempotent demo data for the Quality Management module.

Creates quality standards, audits, inspections, improvement actions, and
deliverable sign-offs for the acme and globex tenants. Safe to run repeatedly:
each tenant is guarded by an existence check on QualityStandard, and
auto-numbered records use an existence-checked number helper.

Usage:
    python manage.py seed_quality
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.quality.models import (
    DeliverableSignoff,
    ImprovementAction,
    Inspection,
    QualityAudit,
    QualityStandard,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

STANDARD_CATEGORIES = ['process', 'product', 'regulatory', 'industry']
STANDARD_STATUSES = ['draft', 'active', 'retired']
AUDIT_TYPES = ['process', 'compliance', 'internal', 'external']
AUDIT_RESULTS = ['pass', 'conditional', 'fail']
AUDIT_STATUSES = ['planned', 'in_progress', 'completed']
INSPECTION_RESULTS = ['pass', 'fail', 'rework']
INSPECTION_STATUSES = ['scheduled', 'in_progress', 'completed']
IMPROVEMENT_SOURCES = ['audit', 'inspection', 'retrospective', 'feedback']
IMPROVEMENT_STATUSES = ['open', 'in_progress', 'done', 'cancelled']
PRIORITIES = ['low', 'medium', 'high', 'urgent']
SIGNOFF_STATUSES = ['pending', 'approved', 'rejected', 'revisions']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Quality Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if QualityStandard.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (quality) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding quality for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            standards = self._seed_standards(tenant, members, projects)
            audits = self._seed_audits(tenant, members, projects, standards)
            inspections = self._seed_inspections(tenant, members, projects)
            improvements = self._seed_improvements(tenant, members, projects)
            signoffs = self._seed_signoffs(tenant, members, projects)

            self.stdout.write(self.style.SUCCESS(
                f'    Standards: {len(standards)}  Audits: {len(audits)}  '
                f'Inspections: {len(inspections)}  Improvements: {len(improvements)}  '
                f'Sign-offs: {len(signoffs)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nQuality seed complete.'))
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

    # --------------------------------------------------------------- standards
    def _seed_standards(self, tenant, members, projects):
        created = []
        for i in range(6):
            obj = QualityStandard.objects.create(
                tenant=tenant,
                code=f'QS-{random.randint(100, 999)}',
                name=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                description=fake.paragraph(nb_sentences=3),
                category=STANDARD_CATEGORIES[i % len(STANDARD_CATEGORIES)],
                acceptance_criteria=fake.sentence(nb_words=12),
                version=f'{random.randint(1, 3)}.{random.randint(0, 9)}',
                status=STANDARD_STATUSES[i % len(STANDARD_STATUSES)],
                owner=random.choice(members) if members else None,
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------------ audits
    def _seed_audits(self, tenant, members, projects, standards):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(QualityAudit, 'QA')
            if QualityAudit.objects.filter(number=number).exists():
                continue
            obj = QualityAudit.objects.create(
                tenant=tenant,
                number=number,
                title=fake.bs().title()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                standard=random.choice(standards) if standards and random.random() > 0.3 else None,
                audit_date=today - timedelta(days=random.randint(0, 120)),
                auditor=random.choice(members) if members else None,
                audit_type=random.choice(AUDIT_TYPES),
                findings_count=random.randint(0, 12),
                result=random.choice(AUDIT_RESULTS),
                status=AUDIT_STATUSES[i % len(AUDIT_STATUSES)],
                notes=fake.paragraph(nb_sentences=2),
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------- inspections
    def _seed_inspections(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(10):
            number = self._next_number(Inspection, 'QC')
            if Inspection.objects.filter(number=number).exists():
                continue
            obj = Inspection.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                inspection_date=today - timedelta(days=random.randint(0, 90)),
                inspector=random.choice(members) if members else None,
                deliverable=fake.bs().title()[:160],
                defects_found=random.randint(0, 8),
                result=random.choice(INSPECTION_RESULTS),
                status=INSPECTION_STATUSES[i % len(INSPECTION_STATUSES)],
                notes=fake.paragraph(nb_sentences=2),
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------ improvements
    def _seed_improvements(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(ImprovementAction, 'CI')
            if ImprovementAction.objects.filter(number=number).exists():
                continue
            obj = ImprovementAction.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                description=fake.paragraph(nb_sentences=3),
                source=random.choice(IMPROVEMENT_SOURCES),
                priority=random.choice(PRIORITIES),
                owner=random.choice(members) if members else None,
                due_date=today + timedelta(days=random.randint(-15, 60)),
                status=IMPROVEMENT_STATUSES[i % len(IMPROVEMENT_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- sign-offs
    def _seed_signoffs(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(DeliverableSignoff, 'SO')
            if DeliverableSignoff.objects.filter(number=number).exists():
                continue
            status = SIGNOFF_STATUSES[i % len(SIGNOFF_STATUSES)]
            submitted = today - timedelta(days=random.randint(5, 60))
            obj = DeliverableSignoff.objects.create(
                tenant=tenant,
                number=number,
                deliverable_name=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                description=fake.paragraph(nb_sentences=2),
                submitted_by=random.choice(members) if members else None,
                approver=random.choice(members) if members else None,
                submitted_date=submitted,
                signoff_date=(submitted + timedelta(days=random.randint(1, 14)))
                if status in ('approved', 'rejected') else None,
                status=status,
            )
            created.append(obj)
        return created
