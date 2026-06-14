"""Seed idempotent demo data for NavPMS.

Creates global Plans, a superuser, two tenants, and a full set of tenant-scoped
records (users, roles, subscriptions, invoices, projects, tasks, meetings,
tickets, project invoices, financial snapshots, audit logs, etc.).

Idempotent: safe to run repeatedly without --flush. Per CLAUDE.md rules it
guards each tenant with an existence check, uses get_or_create for unique
constraints, and checks existence before creating auto-numbered records.

Usage:
    python manage.py seed_demo
    python manage.py seed_demo --flush     # wipe demo data then re-seed
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from faker import Faker

from apps.accounts.models import Role, UserPreference
from apps.core.models import AuditLog, Tenant
from apps.projects.models import (
    FinancialSnapshot,
    Meeting,
    Project,
    ProjectInvoice,
    Task,
    Ticket,
)
from apps.tenants.models import (
    BrandingSettings,
    Invoice,
    PaymentMethod,
    Plan,
    Subscription,
    SystemAlert,
    UsageMetric,
)

User = get_user_model()

# Deterministic-ish randomness so repeated fresh seeds look stable.
fake = Faker()
Faker.seed(42)
random.seed(42)

TENANTS = [
    {'name': 'Acme Corp', 'slug': 'acme', 'plan': 'professional', 'sub_status': Subscription.STATUS_ACTIVE},
    {'name': 'Globex Inc', 'slug': 'globex', 'plan': 'starter', 'sub_status': Subscription.STATUS_TRIALING},
]

ROLE_SPECS = [
    ('Administrator', 'Full access to all tenant settings and data.', True),
    ('Project Manager', 'Manage projects, tasks, and team members.', False),
    ('Member', 'Standard team member access.', False),
    ('Client', 'Read-only access to assigned projects.', False),
]


class Command(BaseCommand):
    help = 'Seed idempotent demo data (plans, tenants, users, projects, billing).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing demo data before seeding.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self._flush()

        plans = self._seed_plans()
        self._seed_superuser()

        for spec in TENANTS:
            self._seed_tenant(spec, plans)

        self.stdout.write(self.style.SUCCESS('\nSeed complete.'))
        self._print_credentials()

    # ------------------------------------------------------------------ flush
    def _flush(self):
        self.stdout.write(self.style.WARNING('Flushing existing demo data...'))
        # Order matters only loosely thanks to CASCADE; delete child-heavy first.
        AuditLog.objects.all().delete()
        FinancialSnapshot.objects.all().delete()
        ProjectInvoice.objects.all().delete()
        Ticket.objects.all().delete()
        Meeting.objects.all().delete()
        Task.objects.all().delete()
        Project.objects.all().delete()
        SystemAlert.objects.all().delete()
        UsageMetric.objects.all().delete()
        PaymentMethod.objects.all().delete()
        BrandingSettings.objects.all().delete()
        Invoice.objects.all().delete()
        Subscription.objects.all().delete()
        # Remove tenant users (keep the global superuser).
        User.objects.filter(tenant__isnull=False).delete()
        Role.objects.all().delete()
        Tenant.objects.all().delete()
        Plan.objects.all().delete()
        self.stdout.write(self.style.WARNING('Flush done.'))

    # ------------------------------------------------------------------ plans
    def _seed_plans(self):
        specs = [
            {
                'name': 'Starter', 'slug': 'starter',
                'price_monthly': Decimal('19.00'), 'price_yearly': Decimal('190.00'),
                'max_users': 5, 'max_projects': 10, 'max_storage_gb': 5,
                'features': ['Up to 5 users', '10 projects', '5 GB storage', 'Email support'],
                'is_popular': False, 'sort_order': 1,
            },
            {
                'name': 'Professional', 'slug': 'professional',
                'price_monthly': Decimal('49.00'), 'price_yearly': Decimal('490.00'),
                'max_users': 25, 'max_projects': 100, 'max_storage_gb': 50,
                'features': ['Up to 25 users', '100 projects', '50 GB storage',
                             'Priority support', 'Advanced reporting'],
                'is_popular': True, 'sort_order': 2,
            },
            {
                'name': 'Enterprise', 'slug': 'enterprise',
                'price_monthly': Decimal('149.00'), 'price_yearly': Decimal('1490.00'),
                'max_users': 500, 'max_projects': 1000, 'max_storage_gb': 500,
                'features': ['Unlimited users', 'Unlimited projects', '500 GB storage',
                             'Dedicated support', 'SSO & audit logs', 'Custom branding'],
                'is_popular': False, 'sort_order': 3,
            },
        ]
        plans = {}
        for data in specs:
            plan, created = Plan.objects.get_or_create(
                slug=data['slug'],
                defaults={**data, 'is_active': True},
            )
            plans[data['slug']] = plan
            self.stdout.write(f'  Plan {"created" if created else "exists"}: {plan.name}')
        return plans

    # -------------------------------------------------------------- superuser
    def _seed_superuser(self):
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@navpms.local',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Site',
                'last_name': 'Admin',
                'tenant': None,
            },
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        UserPreference.objects.get_or_create(user=admin)
        self.stdout.write(f'  Superuser {"created" if created else "exists"}: admin')
        self.stdout.write(self.style.WARNING(
            '  WARNING: Superuser "admin" has no tenant (tenant=None). '
            'Module data is tenant-scoped, so it will NOT appear when logged in '
            'as admin. Log in as a tenant admin (admin_acme / admin_globex) to see data.'
        ))

    # ----------------------------------------------------------------- tenant
    @transaction.atomic
    def _seed_tenant(self, spec, plans):
        tenant, created = Tenant.objects.get_or_create(
            slug=spec['slug'],
            defaults={
                'name': spec['name'],
                'subdomain': spec['slug'],
                'contact_email': f'contact@{spec["slug"]}.example.com',
                'is_active': True,
            },
        )

        # Idempotency guard (CLAUDE.md): if this tenant already has projects,
        # assume it is fully seeded and skip.
        if not created and tenant.projects.exists():
            self.stdout.write(self.style.WARNING(
                f'  Tenant "{tenant.name}" already seeded - skipping.'
            ))
            return

        self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding tenant: {tenant.name}'))

        roles = self._seed_roles(tenant)
        admin_user, members = self._seed_users(tenant, spec, roles)
        # Set tenant owner to its admin.
        if tenant.owner_id is None:
            tenant.owner = admin_user
            tenant.save(update_fields=['owner'])

        all_members = [admin_user] + members
        self._seed_subscription(tenant, spec, plans)
        self._seed_invoices(tenant)
        self._seed_payment_method(tenant)
        self._seed_usage_metrics(tenant, spec, plans)
        self._seed_branding(tenant)
        self._seed_alerts(tenant)
        self._seed_projects(tenant, all_members)
        self._seed_financial_snapshots(tenant)
        self._seed_audit_logs(tenant, all_members)

    # ------------------------------------------------------------------ roles
    def _seed_roles(self, tenant):
        roles = {}
        for name, description, is_system in ROLE_SPECS:
            role, _ = Role.objects.get_or_create(
                tenant=tenant,
                name=name,
                defaults={
                    'description': description,
                    'is_system': is_system,
                    'permissions': [],
                },
            )
            roles[name] = role
        return roles

    # ------------------------------------------------------------------ users
    def _seed_users(self, tenant, spec, roles):
        admin_role = roles['Administrator']
        admin_username = f'admin_{spec["slug"]}'
        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': f'{admin_username}@{spec["slug"]}.example.com',
                'first_name': 'Tenant',
                'last_name': 'Admin',
                'tenant': tenant,
                'is_tenant_admin': True,
                'is_staff': False,
                'role': admin_role,
                'job_title': 'Administrator',
            },
        )
        if created:
            admin_user.set_password('password123')
            admin_user.save()
        UserPreference.objects.get_or_create(user=admin_user)

        member_roles = [roles['Project Manager'], roles['Member'], roles['Client']]
        members = []
        count = random.randint(3, 6)
        for i in range(count):
            first = fake.first_name()
            last = fake.last_name()
            base = slugify(f'{first}.{last}') or f'user{i}'
            username = f'{base}_{spec["slug"]}'
            # Ensure uniqueness against existing usernames.
            suffix = 0
            candidate = username
            while User.objects.filter(username=candidate).exists():
                suffix += 1
                candidate = f'{username}{suffix}'
            user, u_created = User.objects.get_or_create(
                username=candidate,
                defaults={
                    'email': f'{base}@{spec["slug"]}.example.com',
                    'first_name': first,
                    'last_name': last,
                    'tenant': tenant,
                    'is_tenant_admin': False,
                    'role': member_roles[i % len(member_roles)],
                    'job_title': fake.job()[:120],
                    'phone': fake.phone_number()[:40],
                },
            )
            if u_created:
                user.set_password('password123')
                user.save()
            UserPreference.objects.get_or_create(user=user)
            members.append(user)
        return admin_user, members

    # ----------------------------------------------------------- subscription
    def _seed_subscription(self, tenant, spec, plans):
        plan = plans[spec['plan']]
        today = timezone.now().date()
        status = spec['sub_status']
        trialing = status == Subscription.STATUS_TRIALING
        Subscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': plan,
                'status': status,
                'billing_cycle': 'monthly',
                'seats': plan.max_users,
                'started_at': today - timedelta(days=120),
                'trial_ends_at': (today + timedelta(days=9)) if trialing else None,
                'current_period_start': today - timedelta(days=10),
                'current_period_end': today + timedelta(days=20),
                'auto_renew': True,
            },
        )

    # --------------------------------------------------------------- invoices
    def _seed_invoices(self, tenant):
        subscription = getattr(tenant, 'subscription', None)
        today = timezone.now().date()
        plan_price = subscription.plan.price_monthly if subscription and subscription.plan else Decimal('49.00')
        statuses = [
            Invoice.STATUS_PAID,
            Invoice.STATUS_PAID,
            Invoice.STATUS_SENT,
            Invoice.STATUS_OVERDUE,
            Invoice.STATUS_DRAFT,
        ]
        for i, status in enumerate(statuses):
            issue = today - timedelta(days=30 * (len(statuses) - i))
            due = issue + timedelta(days=15)
            amount = plan_price
            tax = (amount * Decimal('0.10')).quantize(Decimal('0.01'))
            total = amount + tax
            paid_at = issue + timedelta(days=3) if status == Invoice.STATUS_PAID else None
            # Auto-numbered: check existence before creating (CLAUDE.md rule).
            number = self._next_invoice_number(Invoice, 'INV')
            if Invoice.objects.filter(tenant=tenant, number=number).exists():
                continue
            Invoice.objects.create(
                tenant=tenant,
                subscription=subscription,
                number=number,
                amount=amount,
                tax=tax,
                total=total,
                status=status,
                issue_date=issue,
                due_date=due,
                paid_at=paid_at,
                notes=fake.sentence(nb_words=8),
            )

    @staticmethod
    def _next_invoice_number(model, prefix):
        last = model.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'{prefix}-{seq:05d}'
        while model.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'{prefix}-{seq:05d}'
        return candidate

    # --------------------------------------------------------- payment method
    def _seed_payment_method(self, tenant):
        # WARNING: mock/demo data only. Never store real card data; tokenize via
        # a PCI-compliant gateway (Stripe, Braintree) in production.
        PaymentMethod.objects.get_or_create(
            tenant=tenant,
            type='card',
            last4='4242',
            defaults={
                'brand': 'Visa',
                'exp_month': 12,
                'exp_year': timezone.now().year + 3,
                'holder_name': tenant.name,
                'is_default': True,
            },
        )

    # ---------------------------------------------------------- usage metrics
    def _seed_usage_metrics(self, tenant, spec, plans):
        plan = plans[spec['plan']]
        user_count = User.objects.filter(tenant=tenant).count()
        project_count = max(tenant.projects.count(), random.randint(3, plan.max_projects))
        metrics = [
            {
                'metric': 'users', 'label': 'Team Members',
                'value': Decimal(user_count), 'limit': Decimal(plan.max_users),
                'unit': 'users',
            },
            {
                'metric': 'storage', 'label': 'Storage Used',
                'value': Decimal(str(round(random.uniform(1, plan.max_storage_gb * 0.8), 2))),
                'limit': Decimal(plan.max_storage_gb), 'unit': 'GB',
            },
            {
                'metric': 'projects', 'label': 'Active Projects',
                'value': Decimal(min(project_count, plan.max_projects)),
                'limit': Decimal(plan.max_projects), 'unit': 'projects',
            },
        ]
        period = timezone.now().strftime('%Y-%m')
        for m in metrics:
            UsageMetric.objects.get_or_create(
                tenant=tenant,
                metric=m['metric'],
                period=period,
                defaults={
                    'label': m['label'],
                    'value': m['value'],
                    'limit': m['limit'],
                    'unit': m['unit'],
                },
            )

    # --------------------------------------------------------------- branding
    def _seed_branding(self, tenant):
        BrandingSettings.objects.get_or_create(
            tenant=tenant,
            defaults={
                'primary_color': '#2563eb',
                'secondary_color': '#1e40af',
                'accent_color': '#3b82f6',
                'email_from_name': tenant.name,
                'email_signature': f'The {tenant.name} Team',
                'enable_white_label': False,
            },
        )

    # ----------------------------------------------------------------- alerts
    def _seed_alerts(self, tenant):
        specs = [
            ('info', 'usage', 'Monthly usage report ready',
             'Your usage report for this period is now available.'),
            ('warning', 'billing', 'Payment method expiring soon',
             'A card on file will expire within 60 days. Please update it.'),
            ('critical', 'security', 'Unusual login activity detected',
             'We detected a sign-in from a new location. Review recent activity.'),
            ('warning', 'performance', 'Storage approaching limit',
             'You have used over 70% of your storage allocation.'),
            ('info', 'usage', 'New team member joined',
             'A new member was added to your workspace.'),
        ]
        for severity, category, title, message in specs:
            SystemAlert.objects.get_or_create(
                tenant=tenant,
                title=title,
                defaults={
                    'severity': severity,
                    'category': category,
                    'message': message,
                    'is_resolved': severity == 'info',
                    'resolved_at': timezone.now() if severity == 'info' else None,
                },
            )

    # --------------------------------------------------------------- projects
    def _seed_projects(self, tenant, members):
        project_statuses = ['not_started', 'in_progress', 'in_progress', 'on_hold',
                            'completed', 'completed', 'cancelled']
        priorities = ['low', 'medium', 'high', 'urgent']
        today = timezone.now().date()
        n_projects = random.randint(5, 8)
        for i in range(n_projects):
            status = project_statuses[i % len(project_statuses)]
            if status == 'completed':
                progress = 100
            elif status == 'not_started':
                progress = 0
            elif status == 'cancelled':
                progress = random.randint(10, 60)
            else:
                progress = random.randint(20, 90)
            budget = Decimal(random.randint(20, 200) * 1000)
            spent_ratio = (Decimal(progress) / Decimal('100')) * Decimal(str(round(random.uniform(0.7, 1.1), 2)))
            spent = (budget * spent_ratio).quantize(Decimal('0.01'))
            start = today - timedelta(days=random.randint(30, 240))
            end = start + timedelta(days=random.randint(60, 300))
            owner = random.choice(members)
            project = Project.objects.create(
                tenant=tenant,
                name=fake.catch_phrase()[:160],
                code=f'PRJ-{i + 1:03d}',
                client_name=fake.company()[:160],
                description=fake.paragraph(nb_sentences=3),
                status=status,
                priority=random.choice(priorities),
                progress=progress,
                budget=budget,
                spent=spent,
                start_date=start,
                end_date=end,
                owner=owner,
                is_billable=random.random() > 0.2,
            )
            self._seed_tasks(tenant, project, members)
            self._seed_meetings(tenant, project, members)
            self._seed_tickets(tenant, project, members)
            self._seed_project_invoices(tenant, project)

    def _seed_tasks(self, tenant, project, members):
        task_statuses = ['todo', 'in_progress', 'review', 'done']
        priorities = ['low', 'medium', 'high', 'urgent']
        today = timezone.now().date()
        for j in range(random.randint(4, 8)):
            status = random.choice(task_statuses)
            is_done = status == 'done'
            Task.objects.create(
                tenant=tenant,
                project=project,
                title=fake.sentence(nb_words=5)[:200],
                description=fake.paragraph(nb_sentences=2),
                assignee=random.choice(members),
                status=status,
                priority=random.choice(priorities),
                due_date=today + timedelta(days=random.randint(-15, 45)),
                is_done=is_done,
                completed_at=timezone.now() if is_done else None,
                order=j,
            )

    def _seed_meetings(self, tenant, project, members):
        types = ['standup', 'review', 'planning', 'client', 'retro']
        now = timezone.now()
        for _ in range(random.randint(4, 6)):
            organizer = random.choice(members)
            meeting = Meeting.objects.create(
                tenant=tenant,
                title=f'{project.code} {random.choice(["Sync", "Review", "Planning", "Check-in"])}',
                meeting_type=random.choice(types),
                scheduled_for=now + timedelta(days=random.randint(-10, 20),
                                              hours=random.randint(0, 8)),
                duration_minutes=random.choice([15, 30, 45, 60]),
                location=random.choice(['Zoom', 'Google Meet', 'Conference Room A', 'On-site']),
                organizer=organizer,
                notes=fake.sentence(nb_words=10),
            )
            attendees = random.sample(members, k=min(len(members), random.randint(2, 4)))
            meeting.attendees.set(attendees)

    def _seed_tickets(self, tenant, project, members):
        statuses = ['open', 'in_progress', 'resolved', 'closed']
        priorities = ['low', 'medium', 'high', 'urgent']
        categories = ['bug', 'feature', 'support', 'question']
        for _ in range(random.randint(5, 8)):
            Ticket.objects.create(
                tenant=tenant,
                project=project,
                subject=fake.sentence(nb_words=6)[:200],
                description=fake.paragraph(nb_sentences=3),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                category=random.choice(categories),
                requester=random.choice(members),
                assignee=random.choice(members),
            )

    def _seed_project_invoices(self, tenant, project):
        today = timezone.now().date()
        statuses = ['draft', 'sent', 'partially_paid', 'paid', 'overdue']
        for k in range(random.randint(4, 6)):
            status = statuses[k % len(statuses)]
            amount = Decimal(random.randint(2, 30) * 1000)
            tax = (amount * Decimal('0.08')).quantize(Decimal('0.01'))
            total = amount + tax
            if status == 'paid':
                paid_amount = total
            elif status == 'partially_paid':
                paid_amount = (total * Decimal('0.5')).quantize(Decimal('0.01'))
            else:
                paid_amount = Decimal('0')
            issue = today - timedelta(days=random.randint(5, 120))
            due = issue + timedelta(days=30)
            if status == 'overdue':
                due = today - timedelta(days=random.randint(1, 20))
            number = self._next_invoice_number(ProjectInvoice, 'PINV')
            if ProjectInvoice.objects.filter(tenant=tenant, number=number).exists():
                continue
            ProjectInvoice.objects.create(
                tenant=tenant,
                project=project,
                number=number,
                client_name=project.client_name,
                amount=amount,
                tax=tax,
                total=total,
                status=status,
                issue_date=issue,
                due_date=due,
                paid_amount=paid_amount,
            )

    # ----------------------------------------------------- financial snapshots
    def _seed_financial_snapshots(self, tenant):
        # Exactly 12 monthly snapshots ending at the current month.
        now = timezone.now()
        periods = []
        year, month = now.year, now.month
        for _ in range(12):
            periods.append(f'{year:04d}-{month:02d}')
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        periods.reverse()  # oldest first
        for idx, period in enumerate(periods):
            income = Decimal(random.randint(40, 120) * 1000) + Decimal(idx * 2500)
            expense = (income * Decimal(str(round(random.uniform(0.55, 0.85), 2)))).quantize(Decimal('0.01'))
            FinancialSnapshot.objects.get_or_create(
                tenant=tenant,
                period=period,
                defaults={'income': income, 'expense': expense},
            )

    # ------------------------------------------------------------- audit logs
    def _seed_audit_logs(self, tenant, members):
        actions = [
            ('login', 'User', 'Signed in'),
            ('create', 'Project', 'Created a project'),
            ('update', 'Task', 'Updated a task'),
            ('create', 'Invoice', 'Generated an invoice'),
            ('delete', 'Ticket', 'Removed a ticket'),
        ]
        for action, entity, repr_text in actions:
            AuditLog.objects.get_or_create(
                tenant=tenant,
                action=action,
                entity=entity,
                object_repr=repr_text,
                defaults={
                    'user': random.choice(members),
                    'changes': fake.sentence(nb_words=8),
                    'ip_address': fake.ipv4(),
                },
            )

    # ----------------------------------------------------------- credentials
    def _print_credentials(self):
        self.stdout.write(self.style.SUCCESS('\n=== Login credentials ==='))
        self.stdout.write('  Superuser (NO tenant - module data hidden): admin / admin123')
        self.stdout.write('  Tenant admin (Acme Corp):   admin_acme   / password123')
        self.stdout.write('  Tenant admin (Globex Inc):  admin_globex / password123')
        self.stdout.write('  All Faker members:          <username>   / password123')
        self.stdout.write(self.style.WARNING(
            '  Reminder: log in as a tenant admin to see tenant-scoped data; '
            'the "admin" superuser has tenant=None.'
        ))
