"""Document & Knowledge Management models (tenant-scoped).

Covers the document register (with auto-number DOC), reusable document
templates, document version history with check-out tracking, a knowledge
base of articles (auto-number KB), and document retention policies.
"""
from decimal import Decimal  # noqa: F401  (kept for convention parity across modules)

from django.conf import settings
from django.db import models
from django.utils import timezone  # noqa: F401  (kept for convention parity across modules)


class Document(models.Model):
    """A managed document with category/status/version, auto-number DOC-00001."""

    CATEGORY_CHOICES = [
        ('charter', 'Charter'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('contract', 'Contract'),
        ('spec', 'Specification'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('archived', 'Archived'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='documents',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documents',
    )
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default='other')
    folder = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='owned_documents',
    )
    doc_url = models.URLField(blank=True)
    current_version = models.CharField(max_length=20, blank=True, default='1.0')
    is_confidential = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Document.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'DOC-{seq:05d}'
        while Document.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'DOC-{seq:05d}'
        return candidate


class DocumentTemplate(models.Model):
    """A reusable document template (category/format/body/version)."""

    CATEGORY_CHOICES = [
        ('charter', 'Charter'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('status', 'Status Update'),
        ('other', 'Other'),
    ]
    FORMAT_CHOICES = [
        ('docx', 'Word'),
        ('xlsx', 'Excel'),
        ('pptx', 'PowerPoint'),
        ('md', 'Markdown'),
        ('pdf', 'PDF'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='document_templates',
    )
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default='other')
    doc_format = models.CharField(max_length=8, choices=FORMAT_CHOICES, default='docx')
    body = models.TextField(blank=True)
    version = models.CharField(max_length=20, blank=True, default='1.0')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='document_templates',
    )
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class DocumentVersion(models.Model):
    """A version record for a Document, with check-out tracking."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('superseded', 'Superseded'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='document_versions',
    )
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='versions',
    )
    version_no = models.CharField(max_length=20)
    change_summary = models.TextField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='document_versions',
    )
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='checked_out_versions',
    )
    is_checked_out = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    file_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.document} v{self.version_no}'


class KnowledgeArticle(models.Model):
    """A knowledge-base article, auto-number KB-00001."""

    CATEGORY_CHOICES = [
        ('lesson_learned', 'Lesson Learned'),
        ('how_to', 'How-To'),
        ('faq', 'FAQ'),
        ('policy', 'Policy'),
        ('playbook', 'Playbook'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='knowledge_articles',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='knowledge_articles',
    )
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default='how_to')
    body = models.TextField(blank=True)
    tags = models.CharField(max_length=200, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='knowledge_articles',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = KnowledgeArticle.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'KB-{seq:05d}'
        while KnowledgeArticle.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'KB-{seq:05d}'
        return candidate


class RetentionPolicy(models.Model):
    """A document retention policy (applies-to / period / action / legal hold)."""

    APPLIES_CHOICES = [
        ('all', 'All Documents'),
        ('charter', 'Charters'),
        ('contract', 'Contracts'),
        ('report', 'Reports'),
        ('financial', 'Financial'),
    ]
    ACTION_CHOICES = [
        ('archive', 'Archive'),
        ('delete', 'Delete'),
        ('review', 'Review'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='retention_policies',
    )
    name = models.CharField(max_length=160)
    applies_to = models.CharField(max_length=16, choices=APPLIES_CHOICES, default='all')
    retention_period_months = models.PositiveSmallIntegerField(default=12)
    action_after = models.CharField(max_length=12, choices=ACTION_CHOICES, default='archive')
    legal_hold = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
