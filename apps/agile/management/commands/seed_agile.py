"""Seed idempotent demo data for the Agile & Scrum Management module.

Creates epics, sprints, backlog items, releases, and retrospectives for the
acme and globex tenants. Safe to run repeatedly: each tenant is guarded by an
existence check on Epic, and auto-numbered records use an existence-checked
number helper.

Usage:
    python manage.py seed_agile
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.agile.models import (
    BacklogItem,
    Epic,
    Release,
    Retrospective,
    Sprint,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

EPIC_STATUSES = ['proposed', 'in_progress', 'done', 'cancelled']
PRIORITIES = ['low', 'medium', 'high', 'critical']
SPRINT_STATUSES = ['planned', 'active', 'completed', 'cancelled']
ITEM_TYPES = ['story', 'bug', 'task', 'spike']
ITEM_STATUSES = ['backlog', 'todo', 'in_progress', 'in_review', 'done']
RELEASE_STATUSES = ['planned', 'in_progress', 'released', 'cancelled']
RETRO_STATUSES = ['scheduled', 'completed']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Agile & Scrum Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Epic.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (agile) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding agile for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            epics = self._seed_epics(tenant, members, projects)
            sprints = self._seed_sprints(tenant, projects)
            backlog_items = self._seed_backlog_items(tenant, members, epics, sprints)
            releases = self._seed_releases(tenant, members, projects)
            retrospectives = self._seed_retrospectives(tenant, members, sprints)

            self.stdout.write(self.style.SUCCESS(
                f'    Epics: {len(epics)}  Sprints: {len(sprints)}  '
                f'Backlog items: {len(backlog_items)}  Releases: {len(releases)}  '
                f'Retrospectives: {len(retrospectives)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nAgile seed complete.'))
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

    # ------------------------------------------------------------------ epics
    def _seed_epics(self, tenant, members, projects):
        created = []
        for i in range(10):
            number = self._next_number(Epic, 'EPIC')
            if Epic.objects.filter(number=number).exists():
                continue
            obj = Epic.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                description=fake.paragraph(nb_sentences=3),
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                owner=random.choice(members) if members else None,
                status=EPIC_STATUSES[i % len(EPIC_STATUSES)],
                priority=PRIORITIES[i % len(PRIORITIES)],
                business_value=random.randint(0, 100),
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------------- sprints
    def _seed_sprints(self, tenant, projects):
        created = []
        today = timezone.now().date()
        for i in range(8):
            number = self._next_number(Sprint, 'SPR')
            if Sprint.objects.filter(number=number).exists():
                continue
            start = today - timedelta(days=random.randint(0, 120))
            capacity = random.randint(20, 60)
            committed = random.randint(10, capacity)
            obj = Sprint.objects.create(
                tenant=tenant,
                number=number,
                name=f'Sprint {i + 1} - {fake.word().title()}'[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                goal=fake.sentence(nb_words=8)[:240],
                status=SPRINT_STATUSES[i % len(SPRINT_STATUSES)],
                start_date=start,
                end_date=start + timedelta(days=14),
                capacity_points=capacity,
                committed_points=committed,
                completed_points=random.randint(0, committed),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------- backlog items
    def _seed_backlog_items(self, tenant, members, epics, sprints):
        created = []
        for i in range(10):
            number = self._next_number(BacklogItem, 'BLI')
            if BacklogItem.objects.filter(number=number).exists():
                continue
            obj = BacklogItem.objects.create(
                tenant=tenant,
                number=number,
                title=fake.sentence(nb_words=6)[:160],
                description=fake.paragraph(nb_sentences=2),
                item_type=ITEM_TYPES[i % len(ITEM_TYPES)],
                epic=random.choice(epics) if epics and random.random() > 0.3 else None,
                sprint=random.choice(sprints) if sprints and random.random() > 0.3 else None,
                status=ITEM_STATUSES[i % len(ITEM_STATUSES)],
                priority=random.choice(PRIORITIES),
                story_points=random.choice([1, 2, 3, 5, 8, 13]),
                assignee=random.choice(members) if members else None,
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- releases
    def _seed_releases(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(6):
            number = self._next_number(Release, 'REL')
            if Release.objects.filter(number=number).exists():
                continue
            status = RELEASE_STATUSES[i % len(RELEASE_STATUSES)]
            obj = Release.objects.create(
                tenant=tenant,
                number=number,
                name=f'{fake.word().title()} Release'[:160],
                version=f'{random.randint(1, 4)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                description=fake.paragraph(nb_sentences=2),
                status=status,
                release_date=(today + timedelta(days=random.randint(-60, 90))
                              if random.random() > 0.2 else None),
                release_manager=random.choice(members) if members else None,
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------- retrospectives
    def _seed_retrospectives(self, tenant, members, sprints):
        created = []
        today = timezone.now().date()
        for i in range(6):
            number = self._next_number(Retrospective, 'RETRO')
            if Retrospective.objects.filter(number=number).exists():
                continue
            obj = Retrospective.objects.create(
                tenant=tenant,
                number=number,
                sprint=random.choice(sprints) if sprints and random.random() > 0.3 else None,
                title=f'Retro - {fake.catch_phrase()}'[:160],
                retro_date=today - timedelta(days=random.randint(0, 90)),
                facilitator=random.choice(members) if members else None,
                went_well=fake.paragraph(nb_sentences=2),
                needs_improvement=fake.paragraph(nb_sentences=2),
                action_items=fake.paragraph(nb_sentences=2),
                team_health_score=random.randint(1, 5),
                status=RETRO_STATUSES[i % len(RETRO_STATUSES)],
            )
            created.append(obj)
        return created
