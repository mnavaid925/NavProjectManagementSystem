"""Seed idempotent demo data for the Project Initiation & Charter module.

Creates project requests, business cases, charters, stakeholders, and kickoff
tasks for the acme and globex tenants. Safe to run repeatedly: each tenant is
guarded by an existence check on ProjectRequest, and auto-numbered records use
an existence-checked number helper.

Usage:
    python manage.py seed_initiation
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

from apps.initiation.models import (
    BusinessCase,
    KickoffTask,
    ProjectCharter,
    ProjectRequest,
    Stakeholder,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

REQUEST_STATUSES = ['draft', 'submitted', 'under_review', 'approved', 'rejected']
PRIORITIES = ['low', 'medium', 'high', 'urgent']
BC_STATUSES = ['draft', 'in_review', 'approved', 'rejected']
RECOMMENDATIONS = ['go', 'no_go', 'hold']
CHARTER_STATUSES = ['draft', 'approved', 'active', 'closed']
LEVELS = ['low', 'medium', 'high']
ENGAGEMENTS = ['unaware', 'resistant', 'neutral', 'supportive', 'leading']
KICKOFF_CATEGORIES = ['logistics', 'team', 'comms', 'governance']
KICKOFF_STATUSES = ['pending', 'in_progress', 'done']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Project Initiation & Charter module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if ProjectRequest.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (initiation) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding initiation for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            requests = self._seed_requests(tenant, members, projects)
            cases = self._seed_business_cases(tenant, requests)
            charters = self._seed_charters(tenant, members, projects)
            stakeholders = self._seed_stakeholders(tenant, projects)
            kickoffs = self._seed_kickoff_tasks(tenant, members, projects, charters)

            self.stdout.write(self.style.SUCCESS(
                f'    Requests: {len(requests)}  Business cases: {len(cases)}  '
                f'Charters: {len(charters)}  Stakeholders: {len(stakeholders)}  '
                f'Kickoff tasks: {len(kickoffs)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nInitiation seed complete.'))
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

    # --------------------------------------------------------------- requests
    def _seed_requests(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(ProjectRequest, 'REQ')
            if ProjectRequest.objects.filter(number=number).exists():
                continue
            obj = ProjectRequest.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                department=random.choice(['IT', 'Operations', 'Finance', 'Marketing', 'HR', 'R&D']),
                requested_by=random.choice(members) if members else None,
                description=fake.paragraph(nb_sentences=3),
                expected_benefit=fake.sentence(nb_words=12),
                estimated_budget=Decimal(random.randint(10, 250) * 1000),
                priority=random.choice(PRIORITIES),
                status=REQUEST_STATUSES[i % len(REQUEST_STATUSES)],
                target_start_date=today + timedelta(days=random.randint(15, 120)),
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
            )
            created.append(obj)
        return created

    # --------------------------------------------------------- business cases
    def _seed_business_cases(self, tenant, requests):
        created = []
        for i in range(6):
            number = self._next_number(BusinessCase, 'BC')
            if BusinessCase.objects.filter(number=number).exists():
                continue
            cost = Decimal(random.randint(20, 200) * 1000)
            benefit = cost * Decimal(str(round(random.uniform(1.1, 2.5), 2)))
            obj = BusinessCase.objects.create(
                tenant=tenant,
                number=number,
                title=fake.bs().title()[:160],
                request=random.choice(requests) if requests and random.random() > 0.4 else None,
                summary=fake.paragraph(nb_sentences=2),
                problem_statement=fake.paragraph(nb_sentences=2),
                expected_roi=Decimal(str(round(random.uniform(5, 95), 2))),
                estimated_cost=cost,
                estimated_benefit=benefit.quantize(Decimal('0.01')),
                payback_months=random.randint(6, 36),
                recommendation=random.choice(RECOMMENDATIONS),
                status=BC_STATUSES[i % len(BC_STATUSES)],
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------------- charters
    def _seed_charters(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(5):
            number = self._next_number(ProjectCharter, 'CHTR')
            if ProjectCharter.objects.filter(number=number).exists():
                continue
            status = CHARTER_STATUSES[i % len(CHARTER_STATUSES)]
            start = today - timedelta(days=random.randint(10, 120))
            obj = ProjectCharter.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects else None,
                sponsor=random.choice(members) if members else None,
                project_manager=random.choice(members) if members else None,
                objectives=fake.paragraph(nb_sentences=2),
                scope_summary=fake.paragraph(nb_sentences=2),
                success_criteria=fake.sentence(nb_words=10),
                start_date=start,
                end_date=start + timedelta(days=random.randint(90, 300)),
                budget=Decimal(random.randint(50, 500) * 1000),
                status=status,
                approved_at=start if status in ('approved', 'active', 'closed') else None,
            )
            created.append(obj)
        return created

    # ----------------------------------------------------------- stakeholders
    def _seed_stakeholders(self, tenant, projects):
        created = []
        for _ in range(10):
            obj = Stakeholder.objects.create(
                tenant=tenant,
                name=fake.name()[:150],
                organization=fake.company()[:150],
                role_title=fake.job()[:120],
                email=fake.email(),
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                influence=random.choice(LEVELS),
                interest=random.choice(LEVELS),
                engagement=random.choice(ENGAGEMENTS),
                communication_preference=random.choice(
                    ['Email', 'Phone', 'Weekly meeting', 'Slack', 'Monthly report']
                ),
                notes=fake.sentence(nb_words=10),
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------- kickoff tasks
    def _seed_kickoff_tasks(self, tenant, members, projects, charters):
        created = []
        today = timezone.now().date()
        for _ in range(10):
            status = random.choice(KICKOFF_STATUSES)
            is_complete = status == 'done'
            obj = KickoffTask.objects.create(
                tenant=tenant,
                title=fake.sentence(nb_words=5)[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                charter=random.choice(charters) if charters and random.random() > 0.4 else None,
                description=fake.paragraph(nb_sentences=2),
                owner=random.choice(members) if members else None,
                category=random.choice(KICKOFF_CATEGORIES),
                due_date=today + timedelta(days=random.randint(-10, 30)),
                status=status,
                is_complete=is_complete,
            )
            created.append(obj)
        return created
