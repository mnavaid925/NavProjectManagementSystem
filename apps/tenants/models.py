"""Module 0 - Tenant & Subscription Management models."""
from decimal import Decimal

from django.db import models
from django.utils import timezone


class Plan(models.Model):
    """A subscription plan. System-wide (tenant=None / not tenant-scoped)."""

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    max_users = models.PositiveIntegerField(default=5)
    max_projects = models.PositiveIntegerField(default=10)
    max_storage_gb = models.PositiveIntegerField(default=5)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'price_monthly']

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """A tenant's current subscription (one per tenant)."""

    STATUS_TRIALING = 'trialing'
    STATUS_ACTIVE = 'active'
    STATUS_PAST_DUE = 'past_due'
    STATUS_CANCELED = 'canceled'
    STATUS_EXPIRED = 'expired'
    STATUS_CHOICES = [
        (STATUS_TRIALING, 'Trialing'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PAST_DUE, 'Past Due'),
        (STATUS_CANCELED, 'Canceled'),
        (STATUS_EXPIRED, 'Expired'),
    ]
    BILLING_CHOICES = [('monthly', 'Monthly'), ('yearly', 'Yearly')]

    tenant = models.OneToOneField(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='subscription',
    )
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_TRIALING)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES, default='monthly')
    seats = models.PositiveIntegerField(default=5)
    started_at = models.DateField(default=timezone.now)
    trial_ends_at = models.DateField(null=True, blank=True)
    current_period_start = models.DateField(default=timezone.now)
    current_period_end = models.DateField(default=timezone.now)
    canceled_at = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tenant} - {self.plan} ({self.status})'

    def is_trial(self):
        return self.status == self.STATUS_TRIALING

    def days_left(self):
        end = self.trial_ends_at if self.is_trial() else self.current_period_end
        if not end:
            return 0
        return max((end - timezone.now().date()).days, 0)


class Invoice(models.Model):
    """A billing invoice for a tenant's subscription."""

    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_PAID = 'paid'
    STATUS_OVERDUE = 'overdue'
    STATUS_VOID = 'void'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PAID, 'Paid'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_VOID, 'Void'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='billing_invoices')
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices'
    )
    number = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(default=timezone.now)
    paid_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        if not self.total:
            self.total = Decimal(self.amount or '0') + Decimal(self.tax or '0')
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Invoice.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'INV-{seq:05d}'
        while Invoice.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'INV-{seq:05d}'
        return candidate


class PaymentMethod(models.Model):
    """A stored payment method (MOCK demo data only)."""

    # WARNING: This is mock/demo data only. NEVER store real PANs or card data.
    # In production, tokenize via a PCI-compliant gateway (Stripe, Braintree).
    TYPE_CHOICES = [('card', 'Card'), ('bank', 'Bank'), ('paypal', 'PayPal')]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='card')
    brand = models.CharField(max_length=40, blank=True)
    last4 = models.CharField(max_length=4, blank=True)
    exp_month = models.PositiveSmallIntegerField(null=True, blank=True)
    exp_year = models.PositiveSmallIntegerField(null=True, blank=True)
    holder_name = models.CharField(max_length=120, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.get_type_display()} •••• {self.last4}'.strip()


class UsageMetric(models.Model):
    """A point-in-time usage measurement against a plan limit."""

    METRIC_CHOICES = [
        ('users', 'Users'),
        ('storage', 'Storage'),
        ('api_calls', 'API Calls'),
        ('projects', 'Projects'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='usage_metrics')
    metric = models.CharField(max_length=20, choices=METRIC_CHOICES)
    label = models.CharField(max_length=80, blank=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    limit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    unit = models.CharField(max_length=20, blank=True)
    period = models.CharField(max_length=10, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['metric']

    def __str__(self):
        return f'{self.get_metric_display()}: {self.value}/{self.limit}'

    def percent(self):
        if not self.limit:
            return 0
        return min(int(round(float(self.value) / float(self.limit) * 100)), 100)


class BrandingSettings(models.Model):
    """White-label / branding configuration for a tenant."""

    tenant = models.OneToOneField('core.Tenant', on_delete=models.CASCADE, related_name='branding')
    logo = models.ImageField(upload_to='branding/', null=True, blank=True)
    favicon = models.ImageField(upload_to='branding/', null=True, blank=True)
    primary_color = models.CharField(max_length=9, default='#2563eb')
    secondary_color = models.CharField(max_length=9, default='#1e40af')
    accent_color = models.CharField(max_length=9, default='#3b82f6')
    login_background = models.CharField(max_length=255, blank=True)
    email_from_name = models.CharField(max_length=120, blank=True)
    email_signature = models.TextField(blank=True)
    custom_domain = models.CharField(max_length=120, blank=True)
    enable_white_label = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Branding for {self.tenant}'


class SystemAlert(models.Model):
    """A tenant-level health / security / billing alert."""

    SEVERITY_CHOICES = [('info', 'Info'), ('warning', 'Warning'), ('critical', 'Critical')]
    CATEGORY_CHOICES = [
        ('security', 'Security'),
        ('performance', 'Performance'),
        ('billing', 'Billing'),
        ('usage', 'Usage'),
    ]

    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='system_alerts')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='info')
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='usage')
    title = models.CharField(max_length=160)
    message = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.severity}] {self.title}'
