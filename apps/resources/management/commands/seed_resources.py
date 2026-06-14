"""Seed idempotent demo data for the Resource Management module.

For each tenant (acme, globex) creates skills, resources (with skills M2M),
allocations, team assignments, demand forecasts, and time entries.

Idempotent: guards on `Resource.objects.filter(tenant=tenant).exists()` per
tenant and uses existence-checked auto-numbers for time entries. Safe to run
repeatedly; a second run prints "already seeded - skipping".

Usage:
    python manage.py seed_resources
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
from apps.resources.models import (
    Allocation,
    DemandForecast,
    Resource,
    Skill,
    TeamAssignment,
    TimeEntry,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

SKILL_SPECS = [
    ('Python', 'technical'),
    ('Django', 'technical'),
    ('JavaScript', 'technical'),
    ('Requirements Analysis', 'functional'),
    ('Project Coordination', 'functional'),
    ('Communication', 'soft'),
    ('Leadership', 'soft'),
    ('Financial Services', 'domain'),
]

RESOURCE_TYPES = ['employee', 'employee', 'employee', 'contractor', 'equipment']
ALLOCATION_STATUSES = ['planned', 'active', 'completed']
ASSIGNMENT_STATUSES = ['proposed', 'active', 'released']
FORECAST_STATUSES = ['projected', 'confirmed', 'closed']
TIMEENTRY_STATUSES = ['draft', 'submitted', 'approved', 'rejected']
FORECAST_PERIODS = ['2026-07', '2026-08', '2026-09', '2026-10', '2026-11', '2026-12']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Resource Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Resource.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (resources) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding resources for tenant: {tenant.name}'))
            counts = self._seed_tenant(tenant)
            self.stdout.write(self.style.SUCCESS(
                f'    Skills: {counts["skills"]}, Resources: {counts["resources"]}, '
                f'Allocations: {counts["allocations"]}, Assignments: {counts["assignments"]}, '
                f'Forecasts: {counts["forecasts"]}, TimeEntries: {counts["time_entries"]}'
            ))

        self.stdout.write(self.style.SUCCESS('\nResource Management seed complete.'))
        self.stdout.write(self.style.WARNING(
            '  Reminder: log in as a tenant admin (admin_acme / admin_globex, '
            'password123) to see tenant-scoped data.'
        ))

    # ------------------------------------------------------------------ tenant
    def _seed_tenant(self, tenant):
        members = list(User.objects.filter(tenant=tenant))
        projects = list(Project.objects.filter(tenant=tenant))

        skills = self._seed_skills(tenant)
        resources = self._seed_resources(tenant, members, skills)
        allocations = self._seed_allocations(tenant, resources, projects)
        assignments = self._seed_assignments(tenant, resources, projects)
        forecasts = self._seed_forecasts(tenant, skills, projects)
        time_entries = self._seed_time_entries(tenant, resources, projects)

        return {
            'skills': len(skills),
            'resources': len(resources),
            'allocations': allocations,
            'assignments': assignments,
            'forecasts': forecasts,
            'time_entries': time_entries,
        }

    # ------------------------------------------------------------------ skills
    def _seed_skills(self, tenant):
        skills = []
        for name, category in SKILL_SPECS:
            skill = Skill.objects.create(
                tenant=tenant,
                name=name,
                category=category,
                description=fake.sentence(nb_words=10),
            )
            skills.append(skill)
        return skills

    # --------------------------------------------------------------- resources
    def _seed_resources(self, tenant, members, skills):
        resources = []
        for i in range(10):
            rtype = random.choice(RESOURCE_TYPES)
            is_equipment = rtype == 'equipment'
            name = fake.company() + ' Unit' if is_equipment else fake.name()
            resource = Resource.objects.create(
                tenant=tenant,
                name=name[:150],
                resource_type=rtype,
                email='' if is_equipment else fake.email(),
                job_title='' if is_equipment else fake.job()[:120],
                department=random.choice(['Engineering', 'Delivery', 'Design', 'QA', 'Operations']),
                location=fake.city()[:120],
                capacity_hours_per_week=random.choice([20, 30, 40, 40, 45]),
                cost_rate=Decimal(str(round(random.uniform(35, 180), 2))),
                user=(random.choice(members) if (members and not is_equipment and random.random() > 0.4) else None),
                is_active=random.random() > 0.15,
            )
            if skills:
                resource.skills.set(random.sample(skills, k=random.randint(1, min(4, len(skills)))))
            resources.append(resource)
        return resources

    # ------------------------------------------------------------- allocations
    def _seed_allocations(self, tenant, resources, projects):
        if not resources:
            return 0
        today = timezone.now().date()
        count = 0
        for _ in range(12):
            start = today - timedelta(days=random.randint(0, 60))
            end = start + timedelta(days=random.randint(15, 120))
            Allocation.objects.create(
                tenant=tenant,
                resource=random.choice(resources),
                project=(random.choice(projects) if (projects and random.random() > 0.2) else None),
                allocation_percent=random.randint(25, 120),
                allocated_hours=Decimal(str(round(random.uniform(20, 320), 2))),
                start_date=start,
                end_date=end,
                status=random.choice(ALLOCATION_STATUSES),
                notes=fake.sentence(nb_words=8)[:200],
            )
            count += 1
        return count

    # ------------------------------------------------------------- assignments
    def _seed_assignments(self, tenant, resources, projects):
        if not resources:
            return 0
        today = timezone.now().date()
        count = 0
        for _ in range(8):
            start = today - timedelta(days=random.randint(0, 90))
            end = start + timedelta(days=random.randint(30, 180))
            TeamAssignment.objects.create(
                tenant=tenant,
                resource=random.choice(resources),
                project=(random.choice(projects) if projects else None),
                role_on_project=fake.job()[:120],
                is_lead=random.random() > 0.7,
                start_date=start,
                end_date=end,
                status=random.choice(ASSIGNMENT_STATUSES),
            )
            count += 1
        return count

    # --------------------------------------------------------------- forecasts
    def _seed_forecasts(self, tenant, skills, projects):
        count = 0
        for _ in range(8):
            demand = Decimal(str(round(random.uniform(80, 400), 2)))
            capacity = Decimal(str(round(random.uniform(60, 420), 2)))
            DemandForecast.objects.create(
                tenant=tenant,
                title=f'{fake.bs().title()[:140]} Demand',
                project=(random.choice(projects) if (projects and random.random() > 0.3) else None),
                skill=(random.choice(skills) if skills else None),
                period=random.choice(FORECAST_PERIODS),
                demand_hours=demand,
                capacity_hours=capacity,
                status=random.choice(FORECAST_STATUSES),
                notes=fake.sentence(nb_words=8)[:200],
            )
            count += 1
        return count

    # ------------------------------------------------------------ time entries
    def _seed_time_entries(self, tenant, resources, projects):
        if not resources:
            return 0
        today = timezone.now().date()
        count = 0
        for _ in range(14):
            number = self._next_te_number()
            if TimeEntry.objects.filter(number=number).exists():
                continue
            TimeEntry.objects.create(
                tenant=tenant,
                number=number,
                resource=random.choice(resources),
                project=(random.choice(projects) if (projects and random.random() > 0.2) else None),
                work_date=today - timedelta(days=random.randint(0, 30)),
                hours=Decimal(str(round(random.uniform(1, 9), 2))),
                is_billable=random.random() > 0.2,
                status=random.choice(TIMEENTRY_STATUSES),
                description=fake.sentence(nb_words=8)[:200],
            )
            count += 1
        return count

    @staticmethod
    def _next_te_number():
        last = TimeEntry.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'TE-{seq:05d}'
        while TimeEntry.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'TE-{seq:05d}'
        return candidate
