"""Seed idempotent demo data for the Master Data & Configuration module.

Creates project templates, custom fields, org units, teams, and localization
settings for the acme and globex tenants. Safe to run repeatedly: each tenant
is guarded by an existence check on ProjectTemplate, and auto-numbered records
use an existence-checked number helper.

Usage:
    python manage.py seed_masterdata
"""
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from faker import Faker

from apps.core.models import Tenant

from apps.masterdata.models import (
    CustomField,
    LocalizationSetting,
    OrgUnit,
    ProjectTemplate,
    Team,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

METHODOLOGIES = ['waterfall', 'agile', 'scrum', 'kanban', 'hybrid', 'prince2']
TEMPLATE_STATUSES = ['active', 'draft', 'archived']
TEMPLATE_CATEGORIES = ['Software', 'Construction', 'Marketing', 'Research', 'Operations']
FIELD_TYPES = ['text', 'number', 'date', 'dropdown', 'checkbox', 'textarea']
FIELD_STATUSES = ['active', 'inactive']
ENTITY_TYPES = ['project', 'task', 'risk', 'issue', 'milestone', 'resource']
UNIT_TYPES = ['company', 'division', 'department', 'business_unit', 'location']
ORG_STATUSES = ['active', 'inactive']
TEAM_STATUSES = ['active', 'inactive']
FOCUS_AREAS = ['Backend', 'Frontend', 'QA', 'DevOps', 'Design', 'Data', 'Support']
LOCALE_STATUSES = ['active', 'inactive']
LOCALES = [
    ('en_US', 'English (US)', 'America/New_York', 'MM/DD/YYYY', '1,234.56', 'USD'),
    ('en_GB', 'English (UK)', 'Europe/London', 'DD/MM/YYYY', '1,234.56', 'GBP'),
    ('de_DE', 'German', 'Europe/Berlin', 'DD.MM.YYYY', '1.234,56', 'EUR'),
    ('fr_FR', 'French', 'Europe/Paris', 'DD/MM/YYYY', '1 234,56', 'EUR'),
    ('ja_JP', 'Japanese', 'Asia/Tokyo', 'YYYY/MM/DD', '1,234', 'JPY'),
    ('en_AU', 'English (AU)', 'Australia/Sydney', 'DD/MM/YYYY', '1,234.56', 'AUD'),
    ('en_CA', 'English (CA)', 'America/Toronto', 'YYYY-MM-DD', '1,234.56', 'CAD'),
]


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Master Data & Configuration module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if ProjectTemplate.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (masterdata) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding masterdata for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))

            project_templates = self._seed_project_templates(tenant)
            custom_fields = self._seed_custom_fields(tenant)
            org_units = self._seed_org_units(tenant, members)
            teams = self._seed_teams(tenant, org_units, members)
            localization_settings = self._seed_localization_settings(tenant)

            self.stdout.write(self.style.SUCCESS(
                f'    Project templates: {len(project_templates)}  '
                f'Custom fields: {len(custom_fields)}  Org units: {len(org_units)}  '
                f'Teams: {len(teams)}  Localization settings: {len(localization_settings)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nMaster data seed complete.'))
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

    # ------------------------------------------------------ project templates
    def _seed_project_templates(self, tenant):
        created = []
        for i in range(8):
            number = self._next_number(ProjectTemplate, 'PT')
            if ProjectTemplate.objects.filter(number=number).exists():
                continue
            obj = ProjectTemplate.objects.create(
                tenant=tenant,
                number=number,
                name=fake.catch_phrase()[:160],
                methodology=METHODOLOGIES[i % len(METHODOLOGIES)],
                category=random.choice(TEMPLATE_CATEGORIES),
                default_duration_days=random.choice([14, 30, 60, 90, 120, 180]),
                phase_count=random.randint(2, 8),
                description=fake.paragraph(nb_sentences=2),
                status=TEMPLATE_STATUSES[i % len(TEMPLATE_STATUSES)],
            )
            created.append(obj)
        return created

    # ----------------------------------------------------------- custom fields
    def _seed_custom_fields(self, tenant):
        created = []
        for i in range(8):
            number = self._next_number(CustomField, 'CF')
            if CustomField.objects.filter(number=number).exists():
                continue
            field_type = FIELD_TYPES[i % len(FIELD_TYPES)]
            options = ''
            if field_type == 'dropdown':
                options = ', '.join(fake.words(nb=random.randint(3, 5)))
            obj = CustomField.objects.create(
                tenant=tenant,
                number=number,
                label=fake.word().title() + ' ' + fake.word().title(),
                field_type=field_type,
                entity_type=random.choice(ENTITY_TYPES),
                is_required=random.choice([True, False]),
                options=options,
                help_text=fake.sentence(nb_words=6),
                status=FIELD_STATUSES[i % len(FIELD_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- org units
    def _seed_org_units(self, tenant, members):
        created = []
        for i in range(8):
            number = self._next_number(OrgUnit, 'OU')
            if OrgUnit.objects.filter(number=number).exists():
                continue
            parent = (random.choice(created)
                      if created and random.random() > 0.4 else None)
            obj = OrgUnit.objects.create(
                tenant=tenant,
                number=number,
                name=fake.company()[:160],
                unit_type=UNIT_TYPES[i % len(UNIT_TYPES)],
                parent=parent,
                manager=random.choice(members) if members else None,
                code=f'OU{random.randint(100, 999)}',
                status=ORG_STATUSES[i % len(ORG_STATUSES)],
            )
            created.append(obj)
        return created

    # ------------------------------------------------------------------- teams
    def _seed_teams(self, tenant, org_units, members):
        created = []
        for i in range(8):
            number = self._next_number(Team, 'TM')
            if Team.objects.filter(number=number).exists():
                continue
            obj = Team.objects.create(
                tenant=tenant,
                number=number,
                name=fake.color_name() + ' ' + random.choice(FOCUS_AREAS) + ' Team',
                org_unit=(random.choice(org_units)
                          if org_units and random.random() > 0.3 else None),
                team_lead=random.choice(members) if members else None,
                member_count=random.randint(2, 12),
                focus_area=random.choice(FOCUS_AREAS),
                status=TEAM_STATUSES[i % len(TEAM_STATUSES)],
            )
            created.append(obj)
        return created

    # --------------------------------------------------- localization settings
    def _seed_localization_settings(self, tenant):
        created = []
        for i in range(6):
            number = self._next_number(LocalizationSetting, 'LOC')
            if LocalizationSetting.objects.filter(number=number).exists():
                continue
            locale = LOCALES[i % len(LOCALES)]
            obj = LocalizationSetting.objects.create(
                tenant=tenant,
                number=number,
                locale_code=locale[0],
                language=locale[1],
                timezone=locale[2],
                date_format=locale[3],
                number_format=locale[4],
                currency=locale[5],
                is_default=(i == 0),
                status=LOCALE_STATUSES[i % len(LOCALE_STATUSES)],
            )
            created.append(obj)
        return created
