"""Seed idempotent demo data for the Collaboration & Communication module.

Creates channels, shared documents, meetings, notifications, and activity
entries for the acme and globex tenants. Safe to run repeatedly: each tenant
is guarded by an existence check on Channel, and auto-numbered meetings use an
existence-checked number helper.

Usage:
    python manage.py seed_collaboration
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.collaboration.models import (
    ActivityEntry,
    Channel,
    Meeting,
    Notification,
    SharedDocument,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

CHANNEL_TYPES = ['public', 'private', 'direct', 'announcement']
DOC_TYPES = ['doc', 'sheet', 'slide', 'pdf', 'other']
VISIBILITIES = ['private', 'team', 'public']
MEETING_TYPES = ['standup', 'review', 'planning', 'client', 'retro']
MEETING_STATUSES = ['scheduled', 'completed', 'cancelled']
NOTIFICATION_TYPES = ['info', 'success', 'warning', 'alert']
PRIORITIES = ['low', 'medium', 'high', 'urgent']
ACTIVITY_TYPES = ['create', 'update', 'delete', 'comment', 'status']
ACTIVITY_VERBS = ['created', 'updated', 'commented on', 'closed', 'reopened', 'assigned']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Collaboration & Communication module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Channel.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (collaboration) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding collaboration for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            channels = self._seed_channels(tenant, members, projects)
            documents = self._seed_documents(tenant, members, projects)
            meetings = self._seed_meetings(tenant, members, projects)
            notifications = self._seed_notifications(tenant, members)
            activities = self._seed_activities(tenant, members, projects)

            self.stdout.write(self.style.SUCCESS(
                f'    Channels: {len(channels)}  Documents: {len(documents)}  '
                f'Meetings: {len(meetings)}  Notifications: {len(notifications)}  '
                f'Activities: {len(activities)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nCollaboration seed complete.'))
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

    # --------------------------------------------------------------- channels
    def _seed_channels(self, tenant, members, projects):
        created = []
        for i in range(8):
            obj = Channel.objects.create(
                tenant=tenant,
                name=fake.word().capitalize() + '-' + fake.word(),
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                channel_type=CHANNEL_TYPES[i % len(CHANNEL_TYPES)],
                topic=fake.sentence(nb_words=5)[:200],
                description=fake.paragraph(nb_sentences=2),
                is_archived=random.random() > 0.75,
                member_count=random.randint(2, 30),
                created_by=random.choice(members) if members else None,
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- documents
    def _seed_documents(self, tenant, members, projects):
        created = []
        for i in range(10):
            obj = SharedDocument.objects.create(
                tenant=tenant,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                doc_type=DOC_TYPES[i % len(DOC_TYPES)],
                doc_url=fake.url(),
                visibility=VISIBILITIES[i % len(VISIBILITIES)],
                version=f'{random.randint(1, 4)}.{random.randint(0, 9)}',
                is_locked=random.random() > 0.7,
                shared_by=random.choice(members) if members else None,
                description=fake.paragraph(nb_sentences=2),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- meetings
    def _seed_meetings(self, tenant, members, projects):
        created = []
        now = timezone.now()
        for i in range(8):
            number = self._next_number(Meeting, 'MTG')
            if Meeting.objects.filter(number=number).exists():
                continue
            obj = Meeting.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                meeting_type=MEETING_TYPES[i % len(MEETING_TYPES)],
                scheduled_for=now + timedelta(days=random.randint(-30, 30),
                                              hours=random.randint(0, 8)),
                duration_minutes=random.choice([15, 30, 45, 60, 90]),
                location=random.choice(['Zoom', 'Conference Room A', 'Google Meet',
                                        'Teams', 'Boardroom']),
                organizer=random.choice(members) if members else None,
                agenda=fake.paragraph(nb_sentences=3),
                minutes=fake.paragraph(nb_sentences=2),
                status=MEETING_STATUSES[i % len(MEETING_STATUSES)],
            )
            created.append(obj)
        return created

    # ---------------------------------------------------------- notifications
    def _seed_notifications(self, tenant, members):
        created = []
        for i in range(12):
            obj = Notification.objects.create(
                tenant=tenant,
                title=fake.sentence(nb_words=6)[:160],
                message=fake.paragraph(nb_sentences=2),
                recipient=random.choice(members) if members else None,
                notification_type=NOTIFICATION_TYPES[i % len(NOTIFICATION_TYPES)],
                priority=PRIORITIES[i % len(PRIORITIES)],
                is_read=random.random() > 0.5,
                link=random.choice(['/projects/', '/tasks/', '/meetings/', '']),
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------ activities
    def _seed_activities(self, tenant, members, projects):
        created = []
        now = timezone.now()
        for i in range(12):
            obj = ActivityEntry.objects.create(
                tenant=tenant,
                actor=random.choice(members) if members else None,
                verb=random.choice(ACTIVITY_VERBS),
                activity_type=ACTIVITY_TYPES[i % len(ACTIVITY_TYPES)],
                entity=random.choice(['Task', 'Risk', 'Document', 'Milestone'])
                + f' WRK-{random.randint(1, 99999):05d}',
                description=fake.sentence(nb_words=10),
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                occurred_at=now - timedelta(days=random.randint(0, 14),
                                            hours=random.randint(0, 23)),
            )
            created.append(obj)
        return created
