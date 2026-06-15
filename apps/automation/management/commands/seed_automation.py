"""Seed idempotent demo data for the Workflow & Automation module.

Creates workflow definitions, approval rules, notification rules, recurring
rules, and automation hooks for the acme and globex tenants. Safe to run
repeatedly: each tenant is guarded by an existence check on WorkflowDefinition,
and auto-numbered records use an existence-checked number helper.

Usage:
    python manage.py seed_automation
"""
import hashlib
import random
import secrets
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.automation.models import (
    ApprovalRule,
    AutomationHook,
    NotificationRule,
    RecurringRule,
    WorkflowDefinition,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

TRIGGER_EVENTS = ['on_create', 'on_update', 'on_status_change', 'scheduled', 'manual']
WORKFLOW_STATUSES = ['draft', 'active', 'paused', 'archived']
APPROVAL_STATUSES = ['active', 'inactive']
NOTIF_TRIGGERS = ['due_date', 'status_change', 'assignment', 'mention', 'risk_threshold']
NOTIF_CHANNELS = ['email', 'in_app', 'sms', 'webhook']
NOTIF_STATUSES = ['active', 'inactive']
FREQUENCIES = ['daily', 'weekly', 'biweekly', 'monthly', 'quarterly']
RECURRING_STATUSES = ['active', 'paused']
HOOK_TYPES = ['webhook', 'zapier', 'make', 'custom_script']
HOOK_STATUSES = ['active', 'inactive', 'error']
ENTITY_TYPES = ['Task', 'Project', 'Invoice', 'Risk', 'PurchaseOrder', 'Document']
RECIPIENT_ROLES = ['Project Manager', 'Team Lead', 'Finance', 'QA', 'Stakeholder']
EVENTS = ['task.created', 'project.updated', 'invoice.paid', 'risk.raised', 'status.changed']


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Workflow & Automation module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if WorkflowDefinition.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (automation) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding automation for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            workflows = self._seed_workflows(tenant, members, projects)
            approval_rules = self._seed_approval_rules(tenant, members)
            notification_rules = self._seed_notification_rules(tenant)
            recurring_rules = self._seed_recurring_rules(tenant, members, projects)
            hooks = self._seed_hooks(tenant)

            self.stdout.write(self.style.SUCCESS(
                f'    Workflows: {len(workflows)}  Approval rules: {len(approval_rules)}  '
                f'Notification rules: {len(notification_rules)}  '
                f'Recurring rules: {len(recurring_rules)}  Hooks: {len(hooks)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nAutomation seed complete.'))
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

    # ----------------------------------------------------------- workflows
    def _seed_workflows(self, tenant, members, projects):
        created = []
        for i in range(8):
            number = self._next_number(WorkflowDefinition, 'WF')
            if WorkflowDefinition.objects.filter(number=number).exists():
                continue
            obj = WorkflowDefinition.objects.create(
                tenant=tenant,
                number=number,
                name=fake.bs().title()[:160],
                trigger_event=TRIGGER_EVENTS[i % len(TRIGGER_EVENTS)],
                entity_type=random.choice(ENTITY_TYPES),
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                owner=random.choice(members) if members else None,
                description=fake.paragraph(nb_sentences=2),
                step_count=random.randint(1, 8),
                status=WORKFLOW_STATUSES[i % len(WORKFLOW_STATUSES)],
            )
            created.append(obj)
        return created

    # ------------------------------------------------------- approval rules
    def _seed_approval_rules(self, tenant, members):
        created = []
        for i in range(6):
            number = self._next_number(ApprovalRule, 'APR')
            if ApprovalRule.objects.filter(number=number).exists():
                continue
            threshold = Decimal(random.randint(1000, 100000))
            auto_below = (threshold * Decimal('0.10')).quantize(Decimal('0.01'))
            obj = ApprovalRule.objects.create(
                tenant=tenant,
                number=number,
                name=f'{random.choice(ENTITY_TYPES)} Approval {i + 1}'[:160],
                entity_type=random.choice(ENTITY_TYPES),
                threshold_amount=threshold,
                approver=random.choice(members) if members else None,
                escalation_hours=random.choice([12, 24, 48, 72]),
                auto_approve_below=auto_below,
                status=APPROVAL_STATUSES[i % len(APPROVAL_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------- notification rules
    def _seed_notification_rules(self, tenant):
        created = []
        for i in range(7):
            number = self._next_number(NotificationRule, 'NR')
            if NotificationRule.objects.filter(number=number).exists():
                continue
            obj = NotificationRule.objects.create(
                tenant=tenant,
                number=number,
                name=f'{NOTIF_TRIGGERS[i % len(NOTIF_TRIGGERS)].replace("_", " ").title()} Alert'[:160],
                trigger_event=NOTIF_TRIGGERS[i % len(NOTIF_TRIGGERS)],
                channel=NOTIF_CHANNELS[i % len(NOTIF_CHANNELS)],
                lead_time_hours=random.choice([0, 1, 4, 12, 24, 48]),
                recipient_role=random.choice(RECIPIENT_ROLES),
                status=NOTIF_STATUSES[i % len(NOTIF_STATUSES)],
            )
            created.append(obj)
        return created

    # ------------------------------------------------------ recurring rules
    def _seed_recurring_rules(self, tenant, members, projects):
        created = []
        today = timezone.now().date()
        for i in range(6):
            number = self._next_number(RecurringRule, 'RC')
            if RecurringRule.objects.filter(number=number).exists():
                continue
            obj = RecurringRule.objects.create(
                tenant=tenant,
                number=number,
                name=fake.catch_phrase()[:160],
                frequency=FREQUENCIES[i % len(FREQUENCIES)],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                assignee=random.choice(members) if members else None,
                next_run_date=today + timedelta(days=random.randint(1, 30)),
                task_template=fake.sentence(nb_words=6)[:200],
                status=RECURRING_STATUSES[i % len(RECURRING_STATUSES)],
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------- hooks
    def _seed_hooks(self, tenant):
        created = []
        for i in range(6):
            number = self._next_number(AutomationHook, 'HK')
            if AutomationHook.objects.filter(number=number).exists():
                continue
            # Demo-only placeholder secret. In production never store a raw
            # secret in plaintext - encrypt at rest or store only a reference.
            placeholder_secret = 'demo_' + hashlib.sha256(secrets.token_bytes(16)).hexdigest()[:32]
            obj = AutomationHook.objects.create(
                tenant=tenant,
                number=number,
                name=f'{HOOK_TYPES[i % len(HOOK_TYPES)].replace("_", " ").title()} Hook {i + 1}'[:160],
                hook_type=HOOK_TYPES[i % len(HOOK_TYPES)],
                target_url=fake.url() + 'hooks/' + fake.uuid4(),
                event=random.choice(EVENTS),
                secret=placeholder_secret,
                status=HOOK_STATUSES[i % len(HOOK_STATUSES)],
            )
            created.append(obj)
        return created
