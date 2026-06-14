"""Portfolio & Program Management models (tenant-scoped).

Covers the portfolio/program layer of the PMS: portfolios grouping related
programs, programs grouping related projects, inter-program dependencies,
strategic goals and their alignment, and capacity (demand vs. supply) plans.
"""
from decimal import Decimal  # noqa: F401  (kept for convention parity across modules)

from django.conf import settings
from django.db import models


class Portfolio(models.Model):
    """A portfolio grouping related programs, auto-number PF-00001."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('closed', 'Closed'),
    ]
    HEALTH_CHOICES = [
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='portfolio_portfolios',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    portfolio_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='portfolio_portfolios',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    health = models.CharField(max_length=8, choices=HEALTH_CHOICES, default='green')
    strategic_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    total_budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
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
        last = Portfolio.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'PF-{seq:05d}'
        while Portfolio.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'PF-{seq:05d}'
        return candidate


class Program(models.Model):
    """A program grouping related projects within a portfolio, auto-number PRG-00001."""

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    HEALTH_CHOICES = [
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='portfolio_programs',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='portfolio_programs',
    )
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    program_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='portfolio_programs',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='planning')
    health = models.CharField(max_length=8, choices=HEALTH_CHOICES, default='green')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
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
        last = Program.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'PRG-{seq:05d}'
        while Program.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'PRG-{seq:05d}'
        return candidate


class ProgramDependency(models.Model):
    """A dependency relationship between two programs (no auto-number)."""

    DEPENDENCY_TYPE_CHOICES = [
        ('finish_to_start', 'Finish to Start'),
        ('start_to_start', 'Start to Start'),
        ('finish_to_finish', 'Finish to Finish'),
        ('start_to_finish', 'Start to Finish'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('blocked', 'Blocked'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='portfolio_dependencies',
    )
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name='portfolio_dependencies_from',
    )
    depends_on = models.ForeignKey(
        Program, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='portfolio_dependencies_to',
    )
    dependency_type = models.CharField(
        max_length=16, choices=DEPENDENCY_TYPE_CHOICES, default='finish_to_start',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    lag_days = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.program} -> {self.depends_on}'


class StrategicGoal(models.Model):
    """A strategic goal and its alignment to a portfolio, auto-number SG-00001."""

    CATEGORY_CHOICES = [
        ('growth', 'Growth'),
        ('efficiency', 'Efficiency'),
        ('innovation', 'Innovation'),
        ('compliance', 'Compliance'),
        ('customer', 'Customer'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('active', 'Active'),
        ('achieved', 'Achieved'),
        ('missed', 'Missed'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='portfolio_goals',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='portfolio_goals',
    )
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default='growth')
    alignment_score = models.IntegerField(default=0)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='proposed')
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
        last = StrategicGoal.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'SG-{seq:05d}'
        while StrategicGoal.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'SG-{seq:05d}'
        return candidate


class CapacityPlan(models.Model):
    """A capacity plan comparing demand vs. supply hours for a period, auto-number CP-00001."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE, related_name='portfolio_capacity_plans',
    )
    number = models.CharField(max_length=20, unique=True, blank=True)
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='portfolio_capacity_plans',
    )
    period = models.CharField(max_length=40)
    team = models.CharField(max_length=120, blank=True)
    demand_hours = models.IntegerField(default=0)
    capacity_hours = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.period}'

    @property
    def gap_hours(self):
        return self.capacity_hours - self.demand_hours

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number():
        last = CapacityPlan.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        candidate = f'CP-{seq:05d}'
        while CapacityPlan.objects.filter(number=candidate).exists():
            seq += 1
            candidate = f'CP-{seq:05d}'
        return candidate
