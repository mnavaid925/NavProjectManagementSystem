"""Workflow & Automation models (tenant-scoped).

Covers the automation phase: workflow definitions with triggers, approval
rules with thresholds, notification rules per channel, recurring task rules,
and outbound automation hooks (webhooks/Zapier/Make/custom scripts).
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class WorkflowDefinition(models.Model):
    """A workflow definition bound to a trigger event, auto-number WF-00001."""

    TRIGGER_EVENT_CHOICES = [
        ('on_create', 'On Create'),
        ('on_update', 'On Update'),
        ('on_status_change', 'On Status Change'),
        ('scheduled', 'Scheduled'),
        ('manual', 'Manual'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='automation_workflow_definitions',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    trigger_event = models.CharField(
        max_length=20, choices=TRIGGER_EVENT_CHOICES, default='on_create',
    )
    entity_type = models.CharField(max_length=60)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='automation_workflow_definitions',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='automation_workflowdefinition_owner',
    )
    description = models.TextField(blank=True)
    step_count = models.PositiveIntegerField(default=0)
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
        last = WorkflowDefinition.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'WF-{seq:05d}'
        while WorkflowDefinition.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'WF-{seq:05d}'
        return candidate


class ApprovalRule(models.Model):
    """An approval rule with threshold/escalation, auto-number APR-00001."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='automation_approval_rules',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    entity_type = models.CharField(max_length=60)
    threshold_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='automation_approvalrule_approver',
    )
    escalation_hours = models.PositiveIntegerField(default=24)
    auto_approve_below = models.DecimalField(max_digits=14, decimal_places=2, default=0)
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
        last = ApprovalRule.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'APR-{seq:05d}'
        while ApprovalRule.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'APR-{seq:05d}'
        return candidate


class NotificationRule(models.Model):
    """A notification rule per channel/event, auto-number NR-00001."""

    TRIGGER_EVENT_CHOICES = [
        ('due_date', 'Due Date'),
        ('status_change', 'Status Change'),
        ('assignment', 'Assignment'),
        ('mention', 'Mention'),
        ('risk_threshold', 'Risk Threshold'),
    ]
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('in_app', 'In-App'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='automation_notification_rules',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    trigger_event = models.CharField(
        max_length=20, choices=TRIGGER_EVENT_CHOICES, default='due_date',
    )
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='email')
    lead_time_hours = models.PositiveIntegerField(default=0)
    recipient_role = models.CharField(max_length=80, blank=True)
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
        last = NotificationRule.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'NR-{seq:05d}'
        while NotificationRule.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'NR-{seq:05d}'
        return candidate


class RecurringRule(models.Model):
    """A recurring task rule with a schedule, auto-number RC-00001."""

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='automation_recurring_rules',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='weekly')
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='automation_recurring_rules',
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='automation_recurringrule_assignee',
    )
    next_run_date = models.DateField(null=True, blank=True)
    task_template = models.CharField(max_length=200, blank=True)
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
        last = RecurringRule.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'RC-{seq:05d}'
        while RecurringRule.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'RC-{seq:05d}'
        return candidate


class AutomationHook(models.Model):
    """An outbound automation hook (webhook/Zapier/Make), auto-number HK-00001."""

    HOOK_TYPE_CHOICES = [
        ('webhook', 'Webhook'),
        ('zapier', 'Zapier'),
        ('make', 'Make'),
        ('custom_script', 'Custom Script'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='automation_automation_hooks',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    hook_type = models.CharField(max_length=16, choices=HOOK_TYPE_CHOICES, default='webhook')
    target_url = models.URLField(blank=True)
    event = models.CharField(max_length=80, blank=True)
    # WARNING: storing the secret as plaintext is insecure - encrypt at rest (e.g. Fernet/KMS) or store only a reference; never log or render the raw secret.
    secret = models.CharField(max_length=128, blank=True)
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
        last = AutomationHook.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'HK-{seq:05d}'
        while AutomationHook.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'HK-{seq:05d}'
        return candidate
