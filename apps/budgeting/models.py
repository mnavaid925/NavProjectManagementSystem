"""Cost & Budget Management models (tenant-scoped).

Covers the cost management phase: budgets, control accounts (with EVM
metrics), expenses, cost forecasts, and budget change requests.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]


class Budget(models.Model):
    """A planned budget envelope for a project, with auto-number BUD-00001."""

    CATEGORY_CHOICES = [
        ('labor', 'Labor'),
        ('material', 'Material'),
        ('overhead', 'Overhead'),
        ('contingency', 'Contingency'),
        ('equipment', 'Equipment'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='budgeting_budgets',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgeting_budgets',
    )
    fiscal_year = models.CharField(max_length=9, blank=True)
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='labor')
    planned_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    allocated_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    currency = models.CharField(max_length=3, default='USD')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgeting_budgets_owned',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.name}'

    @property
    def remaining(self):
        return self.planned_amount - self.allocated_amount

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Budget.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'BUD-{seq:05d}'
        while Budget.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'BUD-{seq:05d}'
        return candidate


class ControlAccount(models.Model):
    """An EVM control account aggregating budget/earned-value/actual cost."""

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='budgeting_control_accounts',
    )
    code = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgeting_control_accounts',
    )
    budget = models.ForeignKey(
        Budget, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='control_accounts',
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgeting_control_accounts',
    )
    bac = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    earned_value = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    actual_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code', 'id']

    def __str__(self):
        return f'{self.code} {self.name}'.strip()

    @property
    def cpi(self):
        if self.actual_cost:
            return round(self.earned_value / self.actual_cost, 2)
        return 0

    @property
    def cost_variance(self):
        return self.earned_value - self.actual_cost


class Expense(models.Model):
    """A logged cost or commitment, with auto-number EXP-00001."""

    CATEGORY_CHOICES = [
        ('labor', 'Labor'),
        ('material', 'Material'),
        ('travel', 'Travel'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]
    TYPE_CHOICES = [
        ('commitment', 'Commitment'),
        ('actual', 'Actual'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='budgeting_expenses',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    description = models.CharField(max_length=200)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgeting_expenses',
    )
    control_account = models.ForeignKey(
        ControlAccount, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='expenses',
    )
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='material')
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    expense_date = models.DateField(default=timezone.now)
    vendor = models.CharField(max_length=160, blank=True)
    expense_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='actual')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgeting_expenses',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date', '-id']

    def __str__(self):
        return f'{self.number} — {self.description}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = Expense.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'EXP-{seq:05d}'
        while Expense.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'EXP-{seq:05d}'
        return candidate


class CostForecast(models.Model):
    """A period cost forecast (EAC/ETC) tied to a budget."""

    METHOD_CHOICES = [
        ('cpi_based', 'CPI-Based'),
        ('manual', 'Manual'),
        ('spi_cpi', 'SPI×CPI'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='budgeting_cost_forecasts',
    )
    name = models.CharField(max_length=160)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgeting_cost_forecasts',
    )
    budget = models.ForeignKey(
        Budget, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cost_forecasts',
    )
    period = models.CharField(max_length=10)
    bac = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    eac = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    etc = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    method = models.CharField(max_length=12, choices=METHOD_CHOICES, default='cpi_based')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['period', 'id']

    def __str__(self):
        return f'{self.name} ({self.period})'

    @property
    def vac(self):
        return self.bac - self.eac


class BudgetChange(models.Model):
    """A budget change request (BCR), with auto-number BCR-00001."""

    TYPE_CHOICES = [
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('reallocation', 'Reallocation'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='budgeting_budget_changes',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    budget = models.ForeignKey(
        Budget, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='changes',
    )
    change_type = models.CharField(max_length=14, choices=TYPE_CHOICES, default='increase')
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgeting_budget_changes',
    )
    decided_at = models.DateField(null=True, blank=True)
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
        last = BudgetChange.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'BCR-{seq:05d}'
        while BudgetChange.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'BCR-{seq:05d}'
        return candidate
