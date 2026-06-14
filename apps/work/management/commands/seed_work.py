"""Seed idempotent demo data for the Task & Work Management module.

Creates work items, priority scores, board columns, board cards, and work
dependencies for the acme and globex tenants. Safe to run repeatedly: each
tenant is guarded by an existence check on WorkItem, and auto-numbered work
items use an existence-checked number helper.

Usage:
    python manage.py seed_work
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

from apps.work.models import (
    BoardCard,
    BoardColumn,
    PriorityScore,
    WorkDependency,
    WorkItem,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

ITEM_TYPES = ['task', 'bug', 'story', 'spike', 'chore']
WORKITEM_STATUSES = ['backlog', 'todo', 'in_progress', 'review', 'done', 'blocked']
PRIORITIES = ['low', 'medium', 'high', 'urgent']
COLUMN_TYPES = ['backlog', 'todo', 'in_progress', 'review', 'done']
METHODS = ['moscow', 'wsjf', 'rice', 'eisenhower']
URGENCIES = ['low', 'medium', 'high', 'critical']
DEP_TYPES = [
    'finish_to_start', 'start_to_start', 'finish_to_finish',
    'start_to_finish', 'blocks', 'relates',
]
DEP_STATUSES = ['active', 'resolved']
CARD_COLORS = ['', 'red', 'amber', 'blue', 'green', 'slate', 'purple']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Task & Work Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if WorkItem.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (work) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding work for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            work_items = self._seed_work_items(tenant, members, projects)
            columns = self._seed_columns(tenant, projects)
            scores = self._seed_priority_scores(tenant, members, work_items)
            cards = self._seed_cards(tenant, work_items, columns)
            dependencies = self._seed_dependencies(tenant, work_items)

            self.stdout.write(self.style.SUCCESS(
                f'    Work items: {len(work_items)}  Columns: {len(columns)}  '
                f'Priority scores: {len(scores)}  Cards: {len(cards)}  '
                f'Dependencies: {len(dependencies)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nWork seed complete.'))
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

    # ------------------------------------------------------------ work items
    def _seed_work_items(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(10):
            number = self._next_number(WorkItem, 'WRK')
            if WorkItem.objects.filter(number=number).exists():
                continue
            has_dates = random.random() > 0.4
            start = today - timedelta(days=random.randint(1, 30)) if has_dates else None
            due = (start + timedelta(days=random.randint(3, 21))
                   if start else None)
            obj = WorkItem.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                description=fake.paragraph(nb_sentences=3),
                item_type=ITEM_TYPES[i % len(ITEM_TYPES)],
                status=WORKITEM_STATUSES[i % len(WORKITEM_STATUSES)],
                priority=random.choice(PRIORITIES),
                assignee=random.choice(members) if members and random.random() > 0.2 else None,
                reporter=random.choice(members) if members else None,
                story_points=random.choice([None, 1, 2, 3, 5, 8, 13]),
                estimate_hours=(Decimal(str(random.choice([2, 4, 8, 16, 24, 40])))
                                if random.random() > 0.3 else None),
                start_date=start,
                due_date=due,
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- columns
    def _seed_columns(self, tenant, projects):
        created = []
        column_defs = [
            ('Backlog', 'backlog', 0),
            ('To Do', 'todo', 3),
            ('In Progress', 'in_progress', 5),
            ('Review', 'review', 3),
            ('Done', 'done', 0),
            ('Icebox', 'backlog', 0),
        ]
        for order, (name, ctype, wip) in enumerate(column_defs):
            obj = BoardColumn.objects.create(
                tenant=tenant,
                name=name,
                project=random.choice(projects) if projects and random.random() > 0.5 else None,
                column_type=ctype,
                order=order,
                wip_limit=wip,
                is_done_column=(ctype == 'done'),
                description=fake.sentence(nb_words=6)[:200],
            )
            created.append(obj)
        return created

    # ------------------------------------------------------- priority scores
    def _seed_priority_scores(self, tenant, members, work_items):
        created = []
        if not work_items:
            return created
        for i in range(8):
            business_value = random.randint(1, 10)
            effort = random.randint(1, 10)
            obj = PriorityScore.objects.create(
                tenant=tenant,
                work_item=random.choice(work_items),
                method=METHODS[i % len(METHODS)],
                urgency=URGENCIES[i % len(URGENCIES)],
                business_value=business_value,
                effort=effort,
                score=Decimal(str(round(random.uniform(1, 100), 2))),
                rationale=fake.paragraph(nb_sentences=2),
                scored_by=random.choice(members) if members else None,
            )
            created.append(obj)
        return created

    # ----------------------------------------------------------------- cards
    def _seed_cards(self, tenant, work_items, columns):
        created = []
        today = timezone.now().date()
        for i in range(10):
            planned_start = (today - timedelta(days=random.randint(0, 20))
                             if random.random() > 0.4 else None)
            planned_end = (planned_start + timedelta(days=random.randint(2, 14))
                           if planned_start else None)
            obj = BoardCard.objects.create(
                tenant=tenant,
                title=fake.sentence(nb_words=4)[:160],
                work_item=random.choice(work_items) if work_items and random.random() > 0.2 else None,
                column=random.choice(columns) if columns else None,
                position=i,
                planned_start=planned_start,
                planned_end=planned_end,
                progress=random.randint(0, 100),
                is_blocked=random.random() > 0.7,
                color=random.choice(CARD_COLORS),
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------- dependencies
    def _seed_dependencies(self, tenant, work_items):
        created = []
        if len(work_items) < 2:
            return created
        for i in range(8):
            work_item = random.choice(work_items)
            depends_on = random.choice(work_items)
            while depends_on == work_item:
                depends_on = random.choice(work_items)
            obj = WorkDependency.objects.create(
                tenant=tenant,
                work_item=work_item,
                depends_on=depends_on,
                dependency_type=DEP_TYPES[i % len(DEP_TYPES)],
                status=DEP_STATUSES[i % len(DEP_STATUSES)],
                lag_days=random.choice([0, 0, 1, 2, 3, 5]),
                notes=fake.sentence(nb_words=8)[:200],
            )
            created.append(obj)
        return created
