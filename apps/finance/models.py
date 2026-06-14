"""Financial & Billing Management models (tenant-scoped).

Covers the finance phase: cost centers with budget tracking, client invoices,
payments against invoices, budget-vs-actual records, and currency exchange
rates.
"""
from decimal import Decimal  # noqa: F401  (kept for convention parity across modules)

from django.conf import settings
from django.db import models
from django.utils import timezone


class CostCenter(models.Model):
    """A cost center with budget vs. actual tracking, auto-number CC-00001."""

    COST_CENTER_TYPE_CHOICES = [
        ('department', 'Department'),
        ('project', 'Project'),
        ('overhead', 'Overhead'),
        ('capital', 'Capital'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='finance_cost_centers',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    code = models.CharField(max_length=40, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='finance_cost_centers',
    )
    cost_center_type = models.CharField(
        max_length=12, choices=COST_CENTER_TYPE_CHOICES, default='department',
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
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
        last = CostCenter.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CC-{seq:05d}'
        while CostCenter.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CC-{seq:05d}'
        return candidate

    @property
    def variance(self):
        return self.budget - self.actual_cost


class FinanceInvoice(models.Model):
    """A client invoice with amount/tax/status, auto-number FINV-00001."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('void', 'Void'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='finance_invoices',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    client_name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='finance_invoices',
    )
    cost_center = models.ForeignKey(
        CostCenter, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='invoices',
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
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
        last = FinanceInvoice.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'FINV-{seq:05d}'
        while FinanceInvoice.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'FINV-{seq:05d}'
        return candidate

    @property
    def total(self):
        return self.amount + self.tax_amount


class Payment(models.Model):
    """A payment recorded against an invoice, auto-number PAY-00001."""

    METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('check', 'Check'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='finance_payments',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    invoice = models.ForeignKey(
        FinanceInvoice, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='payments',
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    method = models.CharField(max_length=16, choices=METHOD_CHOICES, default='bank_transfer')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateField(default=timezone.now)
    reference = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.amount}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Payment.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'PAY-{seq:05d}'
        while Payment.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'PAY-{seq:05d}'
        return candidate


class BudgetActual(models.Model):
    """A budget-vs-actual record for a period, auto-number BA-00001."""

    CATEGORY_CHOICES = [
        ('labor', 'Labor'),
        ('materials', 'Materials'),
        ('overhead', 'Overhead'),
        ('travel', 'Travel'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='finance_budget_actuals',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='finance_budget_actuals',
    )
    cost_center = models.ForeignKey(
        CostCenter, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budget_actuals',
    )
    period = models.CharField(max_length=40)
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='labor')
    budget_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.period}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = BudgetActual.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'BA-{seq:05d}'
        while BudgetActual.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'BA-{seq:05d}'
        return candidate

    @property
    def variance(self):
        return self.budget_amount - self.actual_amount


class CurrencyRate(models.Model):
    """A currency exchange rate effective on a date (no auto-number)."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('retired', 'Retired'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='finance_currency_rates',
    )
    base_currency = models.CharField(max_length=3, default='USD')
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=16, decimal_places=6, default=1)
    effective_date = models.DateField(default=timezone.now)
    source = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-effective_date', '-id']

    def __str__(self):
        return f'{self.base_currency}->{self.target_currency} @ {self.rate}'
