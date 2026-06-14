"""Seed idempotent demo data for the Scope & Requirements Management module.

Creates requirements, requirement traces, scope statements, change requests,
and scope verifications for the acme and globex tenants. Safe to run
repeatedly: each tenant is guarded by an existence check on Requirement, and
auto-numbered records use an existence-checked number helper.

Usage:
    python manage.py seed_scope
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.scope.models import (
    ChangeRequest,
    Requirement,
    RequirementTrace,
    ScopeStatement,
    ScopeVerification,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

REQUIREMENT_TYPES = ['functional', 'non_functional', 'business', 'technical', 'user']
MOSCOWS = ['must', 'should', 'could', 'wont']
REQUIREMENT_STATUSES = ['draft', 'approved', 'implemented', 'verified', 'rejected']
TRACE_TYPES = ['forward', 'backward', 'bidirectional']
ARTIFACT_TYPES = ['design', 'test', 'code', 'deliverable']
STATEMENT_STATUSES = ['draft', 'approved', 'baselined']
CR_TYPES = ['add', 'modify', 'remove']
CR_STATUSES = ['submitted', 'under_review', 'approved', 'rejected', 'implemented']
PRIORITIES = ['low', 'medium', 'high', 'urgent']
RESULTS = ['accepted', 'rejected', 'conditional']
VERIFICATION_STATUSES = ['pending', 'completed']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Scope & Requirements Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Requirement.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (scope) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding scope for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            requirements = self._seed_requirements(tenant, members, projects)
            traces = self._seed_traces(tenant, requirements)
            statements = self._seed_statements(tenant, members, projects)
            change_requests = self._seed_change_requests(tenant, members, projects, requirements)
            verifications = self._seed_verifications(tenant, members, projects, statements)

            self.stdout.write(self.style.SUCCESS(
                f'    Requirements: {len(requirements)}  Traces: {len(traces)}  '
                f'Statements: {len(statements)}  Change requests: {len(change_requests)}  '
                f'Verifications: {len(verifications)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nScope seed complete.'))
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

    # ----------------------------------------------------------- requirements
    def _seed_requirements(self, tenant, members, projects):
        created = []
        for i in range(10):
            number = self._next_number(Requirement, 'RQ')
            if Requirement.objects.filter(number=number).exists():
                continue
            obj = Requirement.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                description=fake.paragraph(nb_sentences=3),
                requirement_type=REQUIREMENT_TYPES[i % len(REQUIREMENT_TYPES)],
                moscow=MOSCOWS[i % len(MOSCOWS)],
                source=random.choice(['Stakeholder workshop', 'Client RFP', 'Regulation',
                                      'User interview', 'Architecture review']),
                status=REQUIREMENT_STATUSES[i % len(REQUIREMENT_STATUSES)],
                owner=random.choice(members) if members else None,
            )
            created.append(obj)
        return created

    # ----------------------------------------------------------------- traces
    def _seed_traces(self, tenant, requirements):
        created = []
        if not requirements:
            return created
        for i in range(8):
            obj = RequirementTrace.objects.create(
                tenant=tenant,
                requirement=random.choice(requirements),
                trace_type=TRACE_TYPES[i % len(TRACE_TYPES)],
                linked_artifact=fake.sentence(nb_words=4)[:160],
                artifact_type=ARTIFACT_TYPES[i % len(ARTIFACT_TYPES)],
                verified=random.random() > 0.5,
                notes=fake.sentence(nb_words=8)[:200],
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------- statements
    def _seed_statements(self, tenant, members, projects):
        created = []
        for i in range(6):
            number = self._next_number(ScopeStatement, 'SCP')
            if ScopeStatement.objects.filter(number=number).exists():
                continue
            status = STATEMENT_STATUSES[i % len(STATEMENT_STATUSES)]
            obj = ScopeStatement.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                in_scope=fake.paragraph(nb_sentences=2),
                out_of_scope=fake.paragraph(nb_sentences=2),
                assumptions=fake.paragraph(nb_sentences=2),
                constraints=fake.paragraph(nb_sentences=2),
                deliverables=fake.paragraph(nb_sentences=2),
                status=status,
                approved_by=(random.choice(members) if members and status in ('approved', 'baselined')
                             else None),
            )
            created.append(obj)
        return created

    # -------------------------------------------------------- change requests
    def _seed_change_requests(self, tenant, members, projects, requirements):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(ChangeRequest, 'CR')
            if ChangeRequest.objects.filter(number=number).exists():
                continue
            status = CR_STATUSES[i % len(CR_STATUSES)]
            obj = ChangeRequest.objects.create(
                tenant=tenant,
                number=number,
                title=fake.bs().title()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                requirement=(random.choice(requirements)
                             if requirements and random.random() > 0.4 else None),
                description=fake.paragraph(nb_sentences=2),
                change_type=CR_TYPES[i % len(CR_TYPES)],
                impact_summary=fake.paragraph(nb_sentences=2),
                priority=random.choice(PRIORITIES),
                status=status,
                requested_by=random.choice(members) if members else None,
                decided_at=(today - timedelta(days=random.randint(1, 60))
                            if status in ('approved', 'rejected', 'implemented') else None),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------- verifications
    def _seed_verifications(self, tenant, members, projects, statements):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(ScopeVerification, 'SV')
            if ScopeVerification.objects.filter(number=number).exists():
                continue
            result = RESULTS[i % len(RESULTS)]
            obj = ScopeVerification.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                scope_statement=(random.choice(statements)
                                 if statements and random.random() > 0.3 else None),
                verification_date=today - timedelta(days=random.randint(0, 90)),
                verified_by=random.choice(members) if members else None,
                deliverable=fake.sentence(nb_words=4)[:160],
                result=result,
                scope_creep_flag=random.random() > 0.7,
                notes=fake.paragraph(nb_sentences=2),
                status=VERIFICATION_STATUSES[i % len(VERIFICATION_STATUSES)],
            )
            created.append(obj)
        return created
