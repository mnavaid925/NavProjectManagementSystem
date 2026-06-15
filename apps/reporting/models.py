"""Reporting & Business Intelligence models (tenant-scoped).

Covers the reporting phase: report definitions, report runs against those
definitions, dashboard widgets, executive packs, and data exports.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class ReportDefinition(models.Model):
    """A saved report definition, auto-number RPT-00001."""

    CATEGORY_CHOICES = [
        ('status', 'Status'),
        ('risk', 'Risk'),
        ('financial', 'Financial'),
        ('resource', 'Resource'),
        ('schedule', 'Schedule'),
        ('custom', 'Custom'),
    ]
    DATA_SOURCE_CHOICES = [
        ('projects', 'Projects'),
        ('tasks', 'Tasks'),
        ('risks', 'Risks'),
        ('finance', 'Finance'),
        ('resources', 'Resources'),
        ('timesheets', 'Timesheets'),
    ]
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('team', 'Team'),
        ('tenant', 'Tenant'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='reporting_report_definitions',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='status')
    data_source = models.CharField(max_length=12, choices=DATA_SOURCE_CHOICES, default='projects')
    visibility = models.CharField(max_length=8, choices=VISIBILITY_CHOICES, default='team')
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reporting_report_definitions',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reporting_reportdefinition_owner',
    )
    description = models.TextField(blank=True)
    is_scheduled = models.BooleanField(default=False)
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
        last = ReportDefinition.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'RPT-{seq:05d}'
        while ReportDefinition.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'RPT-{seq:05d}'
        return candidate


class ReportRun(models.Model):
    """An execution of a report definition, auto-number RUN-00001."""

    FORMAT_CHOICES = [
        ('html', 'HTML'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
    ]
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='reporting_report_runs',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    report = models.ForeignKey(
        ReportDefinition, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reporting_reportrun_report',
    )
    run_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reporting_reportrun_run_by',
    )
    format = models.CharField(max_length=8, choices=FORMAT_CHOICES, default='html')
    row_count = models.PositiveIntegerField(default=0)
    duration_ms = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = ReportRun.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'RUN-{seq:05d}'
        while ReportRun.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'RUN-{seq:05d}'
        return candidate


class DashboardWidget(models.Model):
    """A dashboard widget bound to a data source, auto-number WID-00001."""

    WIDGET_TYPE_CHOICES = [
        ('kpi_card', 'KPI Card'),
        ('line_chart', 'Line Chart'),
        ('bar_chart', 'Bar Chart'),
        ('pie_chart', 'Pie Chart'),
        ('table', 'Table'),
        ('gauge', 'Gauge'),
    ]
    DATA_SOURCE_CHOICES = [
        ('projects', 'Projects'),
        ('tasks', 'Tasks'),
        ('risks', 'Risks'),
        ('finance', 'Finance'),
        ('resources', 'Resources'),
        ('timesheets', 'Timesheets'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('hidden', 'Hidden'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='reporting_dashboard_widgets',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    widget_type = models.CharField(max_length=12, choices=WIDGET_TYPE_CHOICES, default='kpi_card')
    metric = models.CharField(max_length=120, blank=True)
    data_source = models.CharField(max_length=12, choices=DATA_SOURCE_CHOICES, default='projects')
    position = models.PositiveIntegerField(default=0)
    refresh_interval = models.PositiveIntegerField(default=60)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reporting_dashboardwidget_owner',
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
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
        last = DashboardWidget.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'WID-{seq:05d}'
        while DashboardWidget.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'WID-{seq:05d}'
        return candidate


class ExecutivePack(models.Model):
    """An executive status pack for a project/period, auto-number EP-00001."""

    RAG_STATUS_CHOICES = [
        ('red', 'Red'),
        ('amber', 'Amber'),
        ('green', 'Green'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='reporting_executive_packs',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reporting_executive_packs',
    )
    period = models.CharField(max_length=40)
    rag_status = models.CharField(max_length=8, choices=RAG_STATUS_CHOICES, default='green')
    summary = models.TextField(blank=True)
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reporting_executivepack_prepared_by',
    )
    published_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
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
        last = ExecutivePack.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'EP-{seq:05d}'
        while ExecutivePack.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'EP-{seq:05d}'
        return candidate


class DataExport(models.Model):
    """A data export job to a destination/format, auto-number EXP-00001."""

    EXPORT_TYPE_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
        ('odata', 'OData'),
        ('rest_api', 'REST API'),
    ]
    DATA_SOURCE_CHOICES = [
        ('projects', 'Projects'),
        ('tasks', 'Tasks'),
        ('risks', 'Risks'),
        ('finance', 'Finance'),
        ('resources', 'Resources'),
        ('timesheets', 'Timesheets'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='reporting_data_exports',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    export_type = models.CharField(max_length=10, choices=EXPORT_TYPE_CHOICES, default='csv')
    destination = models.CharField(max_length=200, blank=True)
    data_source = models.CharField(max_length=12, choices=DATA_SOURCE_CHOICES, default='projects')
    record_count = models.PositiveIntegerField(default=0)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reporting_dataexport_requested_by',
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
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
        last = DataExport.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'EXP-{seq:05d}'
        while DataExport.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'EXP-{seq:05d}'
        return candidate
