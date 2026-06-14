"""Client & External Collaboration models (tenant-scoped).

Covers the client/external-collaboration domain: client portal access,
client feedback, statement-of-work contracts, external vendors, and client
invoices. Mirrors the as-built scope app: plain ``models.Model`` with an
explicit tenant FK, explicit created_at/updated_at timestamps, class-attribute
CHOICES, and auto-number ``save()`` overrides for numbered models.
"""
from decimal import Decimal  # noqa: F401  (kept for convention parity across modules)

from django.conf import settings
from django.db import models
from django.utils import timezone


class ClientAccess(models.Model):
    """A client portal access record, auto-number CA-00001."""

    ACCESS_LEVEL_CHOICES = [
        ('view_only', 'View Only'),
        ('comment', 'Comment'),
        ('approve', 'Approve'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='clients_access_records',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    client_name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='clients_access_records',
    )
    contact_name = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    access_level = models.CharField(max_length=12, choices=ACCESS_LEVEL_CHOICES, default='view_only')
    portal_enabled = models.BooleanField(default=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.client_name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = ClientAccess.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CA-{seq:05d}'
        while ClientAccess.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CA-{seq:05d}'
        return candidate


class ClientFeedback(models.Model):
    """A piece of client feedback / approval, auto-number CF-00001."""

    FEEDBACK_TYPE_CHOICES = [
        ('praise', 'Praise'),
        ('concern', 'Concern'),
        ('request', 'Request'),
        ('approval', 'Approval'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('addressed', 'Addressed'),
        ('closed', 'Closed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='clients_feedback_items',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    client_name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='clients_feedback_items',
    )
    subject = models.CharField(max_length=160)
    feedback_type = models.CharField(max_length=12, choices=FEEDBACK_TYPE_CHOICES, default='request')
    rating = models.IntegerField(default=3)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='new')
    submitted_date = models.DateField(default=timezone.now)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.subject}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = ClientFeedback.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CF-{seq:05d}'
        while ClientFeedback.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CF-{seq:05d}'
        return candidate


class SOWContract(models.Model):
    """A statement-of-work / client contract, auto-number SOW-00001."""

    CONTRACT_TYPE_CHOICES = [
        ('fixed_fee', 'Fixed Fee'),
        ('time_materials', 'Time & Materials'),
        ('retainer', 'Retainer'),
        ('milestone', 'Milestone'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('signed', 'Signed'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='clients_contracts',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    client_name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='clients_contracts',
    )
    contract_type = models.CharField(max_length=16, choices=CONTRACT_TYPE_CHOICES, default='fixed_fee')
    value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    signed_date = models.DateField(null=True, blank=True)
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
        last = SOWContract.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SOW-{seq:05d}'
        while SOWContract.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SOW-{seq:05d}'
        return candidate


class ExternalVendor(models.Model):
    """An external vendor / subcontractor, auto-number VEN-00001."""

    SERVICE_TYPE_CHOICES = [
        ('consulting', 'Consulting'),
        ('development', 'Development'),
        ('design', 'Design'),
        ('infrastructure', 'Infrastructure'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blacklisted', 'Blacklisted'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='clients_vendors',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    contact_name = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    service_type = models.CharField(max_length=16, choices=SERVICE_TYPE_CHOICES, default='consulting')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    rating = models.IntegerField(default=3)
    notes = models.TextField(blank=True)
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
        last = ExternalVendor.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'VEN-{seq:05d}'
        while ExternalVendor.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'VEN-{seq:05d}'
        return candidate


class ClientInvoice(models.Model):
    """A client invoice, auto-number CINV-00001."""

    BILLING_TYPE_CHOICES = [
        ('time_materials', 'Time & Materials'),
        ('fixed_fee', 'Fixed Fee'),
        ('milestone', 'Milestone'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='clients_invoices',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    client_name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='clients_invoices',
    )
    contract = models.ForeignKey(
        SOWContract, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='invoices',
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    billing_type = models.CharField(max_length=16, choices=BILLING_TYPE_CHOICES, default='fixed_fee')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.client_name}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = ClientInvoice.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CINV-{seq:05d}'
        while ClientInvoice.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CINV-{seq:05d}'
        return candidate
