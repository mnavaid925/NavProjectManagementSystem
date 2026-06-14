"""Seed idempotent demo data for the Document & Knowledge Management module.

Creates documents, document templates, document versions, knowledge articles,
and retention policies for the acme and globex tenants. Safe to run
repeatedly: each tenant is guarded by an existence check on Document, and
auto-numbered records use an existence-checked number helper.

Usage:
    python manage.py seed_documents
"""
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from faker import Faker

from apps.core.models import Tenant
from apps.projects.models import Project

from apps.documents.models import (
    Document,
    DocumentTemplate,
    DocumentVersion,
    KnowledgeArticle,
    RetentionPolicy,
)

User = get_user_model()

fake = Faker()
Faker.seed(42)
random.seed(42)

DOC_CATEGORIES = ['charter', 'plan', 'report', 'contract', 'spec', 'other']
DOC_STATUSES = ['draft', 'in_review', 'approved', 'archived']
DOC_FOLDERS = [
    '/Projects/Charters', '/Projects/Plans', '/Projects/Reports',
    '/Contracts', '/Specifications', '/General',
]
DOC_VERSIONS = ['1.0', '1.1', '1.2', '2.0']

TEMPLATE_CATEGORIES = ['charter', 'plan', 'report', 'status', 'other']
TEMPLATE_FORMATS = ['docx', 'xlsx', 'pptx', 'md', 'pdf']

VERSION_NOS = ['1.0', '1.1', '2.0']
VERSION_STATUSES = ['draft', 'published', 'superseded']

KB_CATEGORIES = ['lesson_learned', 'how_to', 'faq', 'policy', 'playbook']
KB_STATUSES = ['draft', 'published', 'archived']

APPLIES_TO = ['all', 'charter', 'contract', 'report', 'financial']
ACTIONS = ['archive', 'delete', 'review']
RETENTION_MONTHS = [12, 24, 36, 84]


class Command(BaseCommand):
    help = 'Seed idempotent demo data for the Document & Knowledge Management module.'

    def handle(self, *args, **options):
        for slug in ('acme', 'globex'):
            tenant = Tenant.objects.filter(slug=slug).first()
            if not tenant:
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{slug}" not found - run seed_demo first. Skipping.'
                ))
                continue

            if Document.objects.filter(tenant=tenant).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Tenant "{tenant.name}" already seeded (documents) - skipping.'
                ))
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n  Seeding documents for: {tenant.name}'))

            members = list(User.objects.filter(tenant=tenant))
            projects = list(Project.objects.filter(tenant=tenant))

            documents = self._seed_documents(tenant, members, projects)
            templates = self._seed_templates(tenant, members)
            versions = self._seed_versions(tenant, members, documents)
            articles = self._seed_articles(tenant, members, projects)
            policies = self._seed_policies(tenant)

            self.stdout.write(self.style.SUCCESS(
                f'    Documents: {len(documents)}  Templates: {len(templates)}  '
                f'Versions: {len(versions)}  Knowledge articles: {len(articles)}  '
                f'Retention policies: {len(policies)}'
            ))

        self.stdout.write(self.style.SUCCESS('\nDocuments seed complete.'))
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

    # -------------------------------------------------------------- documents
    def _seed_documents(self, tenant, members, projects):
        created = []
        for i in range(10):
            number = self._next_number(Document, 'DOC')
            if Document.objects.filter(number=number).exists():
                continue
            obj = Document.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.3 else None,
                category=DOC_CATEGORIES[i % len(DOC_CATEGORIES)],
                folder=random.choice(DOC_FOLDERS),
                status=DOC_STATUSES[i % len(DOC_STATUSES)],
                owner=random.choice(members) if members else None,
                doc_url=fake.url(),
                current_version=random.choice(DOC_VERSIONS),
                is_confidential=random.random() > 0.7,
                description=fake.paragraph(nb_sentences=3),
            )
            created.append(obj)
        return created

    # -------------------------------------------------------------- templates
    def _seed_templates(self, tenant, members):
        created = []
        for i in range(6):
            obj = DocumentTemplate.objects.create(
                tenant=tenant,
                name=f'{fake.catch_phrase()[:140]} Template',
                category=TEMPLATE_CATEGORIES[i % len(TEMPLATE_CATEGORIES)],
                doc_format=TEMPLATE_FORMATS[i % len(TEMPLATE_FORMATS)],
                body=fake.paragraph(nb_sentences=4),
                version=random.choice(['1.0', '1.1', '2.0']),
                is_active=random.random() > 0.15,
                created_by=random.choice(members) if members else None,
                description=fake.sentence(nb_words=8)[:200],
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- versions
    def _seed_versions(self, tenant, members, documents):
        created = []
        if not documents:
            return created
        for i in range(10):
            checked_out = random.random() > 0.6
            obj = DocumentVersion.objects.create(
                tenant=tenant,
                document=random.choice(documents),
                version_no=VERSION_NOS[i % len(VERSION_NOS)],
                change_summary=fake.sentence(nb_words=10),
                author=random.choice(members) if members else None,
                checked_out_by=(random.choice(members)
                                if checked_out and members else None),
                is_checked_out=checked_out,
                status=VERSION_STATUSES[i % len(VERSION_STATUSES)],
                file_url=fake.url(),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- articles
    def _seed_articles(self, tenant, members, projects):
        created = []
        for i in range(8):
            number = self._next_number(KnowledgeArticle, 'KB')
            if KnowledgeArticle.objects.filter(number=number).exists():
                continue
            obj = KnowledgeArticle.objects.create(
                tenant=tenant,
                number=number,
                title=fake.catch_phrase()[:160],
                project=random.choice(projects) if projects and random.random() > 0.4 else None,
                category=KB_CATEGORIES[i % len(KB_CATEGORIES)],
                body=fake.paragraph(nb_sentences=5),
                tags=', '.join(fake.words(nb=random.randint(2, 4)))[:200],
                author=random.choice(members) if members else None,
                status=KB_STATUSES[i % len(KB_STATUSES)],
                views_count=random.randint(0, 500),
            )
            created.append(obj)
        return created

    # --------------------------------------------------------------- policies
    def _seed_policies(self, tenant):
        created = []
        for i in range(5):
            obj = RetentionPolicy.objects.create(
                tenant=tenant,
                name=f'{APPLIES_TO[i % len(APPLIES_TO)].title()} Retention Policy',
                applies_to=APPLIES_TO[i % len(APPLIES_TO)],
                retention_period_months=random.choice(RETENTION_MONTHS),
                action_after=ACTIONS[i % len(ACTIONS)],
                legal_hold=random.random() > 0.7,
                is_active=random.random() > 0.1,
                description=fake.paragraph(nb_sentences=2),
            )
            created.append(obj)
        return created
