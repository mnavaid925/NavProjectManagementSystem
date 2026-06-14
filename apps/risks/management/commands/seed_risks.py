"""Seed idempotent demo data for the Risk & Issue Management module.

Creates risks, risk analyses, risk responses, issues, and risk reviews for the
acme and globex tenants. Safe to run repeatedly: each tenant is guarded by an
existence check on Risk, and auto-numbered records use an existence-checked
number helper.

Usage:
    python manage.py seed_risks
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

from apps.risks.models import Issue, Risk, RiskAnalysis, RiskResponse, RiskReview

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

RISK_CATEGORIES = ['technical', 'external', 'organizational', 'pm', 'financial']
RISK_STATUSES = ['open', 'mitigating', 'closed', 'occurred']
LEVELS = ['low', 'medium', 'high']
ANALYSIS_TYPES = ['qualitative', 'quantitative']
ANALYSIS_LEVELS = ['low', 'medium', 'high', 'critical']
RESPONSE_STRATEGIES = ['avoid', 'transfer', 'mitigate', 'accept', 'escalate']
RESPONSE_STATUSES = ['planned', 'in_progress', 'completed']
ISSUE_SEVERITIES = ['low', 'medium', 'high', 'critical']
ISSUE_PRIORITIES = ['low', 'medium', 'high', 'urgent']
ISSUE_STATUSES = ['open', 'in_progress', 'escalated', 'resolved', 'closed']
REVIEW_STATUSES = ['scheduled', 'completed']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Risk & Issue Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Risk.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (risks) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding risks for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            risks = self._seed_risks(tenant, members, projects)
            analyses = self._seed_analyses(tenant, members, risks)
            responses = self._seed_responses(tenant, members, risks)
            issues = self._seed_issues(tenant, members, projects)
            reviews = self._seed_reviews(tenant, members, projects, risks)

            self.stdout.write(self.style.SUCCESS(
                f'    Risks: {len(risks)}  Analyses: {len(analyses)}  '
                f'Responses: {len(responses)}  Issues: {len(issues)}  '
                f'Reviews: {len(reviews)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nRisks seed complete.'))
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

    # -------------------------------------------------------------------- risks
    def _seed_risks(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(10):
            number = self._next_number(Risk, 'RSK')
            if Risk.objects.filter(number=number).exists():
                continue
            obj = Risk.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                description=fake.paragraph(nb_sentences=3),
                category=random.choice(RISK_CATEGORIES),
                probability=random.choice(LEVELS),
                impact=random.choice(LEVELS),
                status=RISK_STATUSES[i % len(RISK_STATUSES)],
                owner=random.choice(members) if members else None,
                identified_date=today - timedelta(days=random.randint(5, 120)),
            )
            created.append(obj)
        return created

    # ----------------------------------------------------------------- analyses
    def _seed_analyses(self, tenant, members, risks):
        created = []
        if not risks:
            return created
        for _ in range(8):
            obj = RiskAnalysis.objects.create(
                tenant=tenant,
                risk=random.choice(risks),
                analysis_type=random.choice(ANALYSIS_TYPES),
                probability_pct=random.randint(5, 95),
                impact_cost=Decimal(random.randint(5, 250) * 1000),
                risk_level=random.choice(ANALYSIS_LEVELS),
                notes=fake.paragraph(nb_sentences=2),
                analyzed_by=random.choice(members) if members else None,
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------------- responses
    def _seed_responses(self, tenant, members, risks):
        created = []
        if not risks:
            return created
        for _ in range(8):
            obj = RiskResponse.objects.create(
                tenant=tenant,
                risk=random.choice(risks),
                strategy=random.choice(RESPONSE_STRATEGIES),
                description=fake.paragraph(nb_sentences=2),
                action_owner=random.choice(members) if members else None,
                planned_action=fake.sentence(nb_words=8)[:200],
                cost=Decimal(random.randint(1, 50) * 1000),
                trigger_condition=fake.sentence(nb_words=8)[:200],
                status=random.choice(RESPONSE_STATUSES),
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------------- issues
    def _seed_issues(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(10):
            number = self._next_number(Issue, 'ISS')
            if Issue.objects.filter(number=number).exists():
                continue
            status = ISSUE_STATUSES[i % len(ISSUE_STATUSES)]
            raised = today - timedelta(days=random.randint(2, 90))
            resolved = (
                raised + timedelta(days=random.randint(1, 30))
                if status in ('resolved', 'closed') else None
            )
            obj = Issue.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                description=fake.paragraph(nb_sentences=3),
                severity=random.choice(ISSUE_SEVERITIES),
                priority=random.choice(ISSUE_PRIORITIES),
                status=status,
                assigned_to=random.choice(members) if members else None,
                raised_date=raised,
                resolved_date=resolved,
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------------ reviews
    def _seed_reviews(self, tenant, members, projects, risks):
        created = []
        today = timezone.now().date()
        for i in range(5):
            obj = RiskReview.objects.create(
                tenant=tenant,
                title=fake.sentence(nb_words=5)[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                review_date=today - timedelta(days=random.randint(-15, 60)),
                reviewed_by=random.choice(members) if members else None,
                summary=fake.paragraph(nb_sentences=3),
                risks_reviewed=len(risks),
                top_risk=random.choice(risks) if risks else None,
                status=REVIEW_STATUSES[i % len(REVIEW_STATUSES)],
            )
            created.append(obj)
        return created
