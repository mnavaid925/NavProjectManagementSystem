"""Master Data & Configuration models (tenant-scoped).

Covers reusable project templates, custom field definitions, the org-unit
hierarchy, teams, and localization settings used to configure the workspace.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class ProjectTemplate(models.Model):
    """A reusable project template, auto-number PT-00001."""

    METHODOLOGY_CHOICES = [
        ('waterfall', 'Waterfall'),
        ('agile', 'Agile'),
        ('scrum', 'Scrum'),
        ('kanban', 'Kanban'),
        ('hybrid', 'Hybrid'),
        ('prince2', 'PRINCE2'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='masterdata_project_templates',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    methodology = models.CharField(
        max_length=12, choices=METHODOLOGY_CHOICES, default='agile',
    )
    category = models.CharField(max_length=80, blank=True)
    default_duration_days = models.PositiveIntegerField(default=30)
    phase_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = ProjectTemplate.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'PT-{seq:05d}'
        while ProjectTemplate.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'PT-{seq:05d}'
        return candidate


class CustomField(models.Model):
    """A custom field definition for an entity, auto-number CF-00001."""

    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('dropdown', 'Dropdown'),
        ('checkbox', 'Checkbox'),
        ('textarea', 'Text Area'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='masterdata_custom_fields',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    label = models.CharField(max_length=120)
    field_type = models.CharField(
        max_length=10, choices=FIELD_TYPE_CHOICES, default='text',
    )
    entity_type = models.CharField(max_length=60)
    is_required = models.BooleanField(default=False)
    options = models.CharField(max_length=255, blank=True)
    help_text = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.label}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = CustomField.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CF-{seq:05d}'
        while CustomField.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CF-{seq:05d}'
        return candidate


class OrgUnit(models.Model):
    """An organizational unit in the org hierarchy, auto-number OU-00001."""

    UNIT_TYPE_CHOICES = [
        ('company', 'Company'),
        ('division', 'Division'),
        ('department', 'Department'),
        ('business_unit', 'Business Unit'),
        ('location', 'Location'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='masterdata_org_units',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    unit_type = models.CharField(
        max_length=16, choices=UNIT_TYPE_CHOICES, default='department',
    )
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='masterdata_child_units',
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='masterdata_orgunit_manager',
    )
    code = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = OrgUnit.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'OU-{seq:05d}'
        while OrgUnit.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'OU-{seq:05d}'
        return candidate


class Team(models.Model):
    """A team belonging to an org unit, auto-number TM-00001."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='masterdata_teams',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    org_unit = models.ForeignKey(
        OrgUnit, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='masterdata_team_org_unit',
    )
    team_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='masterdata_team_team_lead',
    )
    member_count = models.PositiveIntegerField(default=0)
    focus_area = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Team.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'TM-{seq:05d}'
        while Team.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'TM-{seq:05d}'
        return candidate


class LocalizationSetting(models.Model):
    """A localization / locale configuration, auto-number LOC-00001."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='masterdata_localization_settings',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    locale_code = models.CharField(max_length=10)
    language = models.CharField(max_length=60)
    timezone = models.CharField(max_length=60)
    date_format = models.CharField(max_length=40)
    number_format = models.CharField(max_length=40, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    is_default = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.locale_code}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = LocalizationSetting.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'LOC-{seq:05d}'
        while LocalizationSetting.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'LOC-{seq:05d}'
        return candidate
