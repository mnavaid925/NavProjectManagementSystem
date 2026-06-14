"""Seed idempotent demo data for the Project Planning & Scheduling module.

For each demo tenant (acme, globex) this creates work packages, schedule tasks,
task dependencies, milestones, and schedule baselines using Faker data.

Idempotent: guarded on WorkPackage existence per tenant, so it is safe to run
repeatedly without --flush (a second run prints "already seeded - skipping").

Usage:
    python manage.py seed_planning
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.planning.models import (
    Milestone,
    ScheduleBaseline,
    ScheduleTask,
    TaskDependency,
    WorkPackage,
)
from apps.projects.models import Project

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

WP_STATUSES = ['not_started', 'in_progress', 'completed']
TASK_STATUSES = ['not_started', 'in_progress', 'completed', 'blocked']
ESTIMATE_METHODS = ['analogous', 'parametric', 'bottom_up', 'three_point']
DEP_TYPES = ['FS', 'SS', 'FF', 'SF']
MILESTONE_TYPES = ['milestone', 'phase_gate']
GATE_STATUSES = ['pending', 'passed', 'failed']
BASELINE_STATUSES = ['draft', 'approved', 'superseded']

# Sample WBS code / level pairs giving a small hierarchy feel.
WP_CODES = [
    ('1', 1), ('1.1', 2), ('1.2', 2), ('2', 1),
    ('2.1', 2), ('2.2', 2), ('3', 1), ('3.1', 2),
]


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Project Planning & Scheduling module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if WorkPackage.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (planning) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding planning for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            work_packages = self._seed_work_packages(tenant, members, projects)
            tasks = self._seed_tasks(tenant, members, projects, work_packages)
            dependencies = self._seed_dependencies(tenant, tasks)
            milestones = self._seed_milestones(tenant, projects)
            baselines = self._seed_baselines(tenant, projects)

            self.stdout.write(self.style.SUCCESS(
                f'    {tenant.name}: {len(work_packages)} work packages, '
                f'{len(tasks)} tasks, {len(dependencies)} dependencies, '
                f'{len(milestones)} milestones, {len(baselines)} baselines.'
            ))

        self.stdout.write(self.style.SUCCESS('\nPlanning seed complete.'))
        self.stdout.write(self.style.WARNING(
            '  Reminder: log in as a tenant admin (admin_acme / admin_globex, '
            'password123) to see planning data. The "admin" superuser has no tenant.'
        ))

    # ----------------------------------------------------------- work packages
    def _seed_work_packages(self, tenant, members, projects):
        created = []
        parent = None
        for code, level in WP_CODES:
            owner = random.choice(members) if members else None
            project = random.choice(projects) if projects and random.random() > 0.3 else None
            wp = WorkPackage.objects.create(
                tenant=tenant,
                code=code,
                name=fake.catch_phrase()[:160],
                project=project,
                parent=parent if level > 1 else None,
                description=fake.paragraph(nb_sentences=2),
                level=level,
                estimated_effort_hours=Decimal(random.randint(8, 320)),
                owner=owner,
                status=random.choice(WP_STATUSES),
            )
            created.append(wp)
            if level == 1:
                parent = wp
        return created

    # ------------------------------------------------------------------- tasks
    def _seed_tasks(self, tenant, members, projects, work_packages):
        created = []
        today = timezone.now().date()
        for _ in range(12):
            status = random.choice(TASK_STATUSES)
            if status == 'completed':
                percent = 100
            elif status == 'not_started':
                percent = 0
            else:
                percent = random.randint(10, 90)
            start = today + timedelta(days=random.randint(-30, 30))
            duration = random.randint(1, 20)
            wp = random.choice(work_packages) if work_packages and random.random() > 0.3 else None
            project = random.choice(projects) if projects and random.random() > 0.3 else None
            task = ScheduleTask.objects.create(
                tenant=tenant,
                name=fake.sentence(nb_words=5)[:160],
                project=project,
                work_package=wp,
                description=fake.paragraph(nb_sentences=2),
                assignee=random.choice(members) if members else None,
                start_date=start,
                end_date=start + timedelta(days=duration),
                duration_days=duration,
                effort_hours=Decimal(random.randint(4, 160)),
                estimate_method=random.choice(ESTIMATE_METHODS),
                percent_complete=percent,
                status=status,
                is_critical=random.random() > 0.6,
            )
            created.append(task)
        return created

    # ------------------------------------------------------------ dependencies
    def _seed_dependencies(self, tenant, tasks):
        created = []
        if len(tasks) < 2:
            return created
        for _ in range(6):
            predecessor, successor = random.sample(tasks, 2)
            dep = TaskDependency.objects.create(
                tenant=tenant,
                predecessor=predecessor,
                successor=successor,
                dependency_type=random.choice(DEP_TYPES),
                lag_days=random.randint(-2, 5),
                notes=fake.sentence(nb_words=8)[:200],
            )
            created.append(dep)
        return created

    # -------------------------------------------------------------- milestones
    def _seed_milestones(self, tenant, projects):
        created = []
        today = timezone.now().date()
        for _ in range(6):
            mtype = random.choice(MILESTONE_TYPES)
            gate = random.choice(GATE_STATUSES)
            project = random.choice(projects) if projects and random.random() > 0.3 else None
            milestone = Milestone.objects.create(
                tenant=tenant,
                name=fake.bs().title()[:160],
                project=project,
                description=fake.paragraph(nb_sentences=2),
                due_date=today + timedelta(days=random.randint(-30, 120)),
                milestone_type=mtype,
                gate_status=gate,
                entry_criteria=fake.sentence(nb_words=10),
                exit_criteria=fake.sentence(nb_words=10),
                is_completed=gate == 'passed',
            )
            created.append(milestone)
        return created

    # --------------------------------------------------------------- baselines
    def _seed_baselines(self, tenant, projects):
        created = []
        today = timezone.now().date()
        for i in range(4):
            is_current = i == 0  # exactly one current baseline per tenant
            status = 'approved' if is_current else random.choice(BASELINE_STATUSES)
            project = random.choice(projects) if projects and random.random() > 0.3 else None
            start = today - timedelta(days=random.randint(30, 180))
            baseline = ScheduleBaseline.objects.create(
                tenant=tenant,
                name=f'{fake.word().title()} Baseline',
                project=project,
                version=f'v{i + 1}.0',
                baseline_date=today - timedelta(days=random.randint(0, 90)),
                planned_start=start,
                planned_finish=start + timedelta(days=random.randint(60, 300)),
                status=status,
                is_current=is_current,
                notes=fake.sentence(nb_words=10),
            )
            created.append(baseline)
        return created
