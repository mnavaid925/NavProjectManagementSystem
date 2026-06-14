"""Reference dashboard view: aggregates tenant data for KPI cards and charts."""
import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.models import User
from apps.projects.models import (
    FinancialSnapshot,
    Meeting,
    Project,
    ProjectInvoice,
    Task,
    Ticket,
)


@login_required
def index(request):
    tenant = request.tenant
    today = timezone.now().date()

    # ----- KPI cards -----
    projects_qs = Project.objects.filter(tenant=tenant)
    tasks_qs = Task.objects.filter(tenant=tenant)
    project_invoices_qs = ProjectInvoice.objects.filter(tenant=tenant)
    tickets_qs = Ticket.objects.filter(tenant=tenant)

    kpis = {
        'total_projects': projects_qs.count(),
        'active_tasks': tasks_qs.exclude(status='done').count(),
        'overdue_invoices': project_invoices_qs.filter(status='overdue').count(),
        'team_members': User.objects.filter(tenant=tenant).count(),
    }

    # ----- Projects overview (donut) -----
    status_labels = dict(Project.STATUS_CHOICES)
    overview_counts = {key: 0 for key, _ in Project.STATUS_CHOICES}
    for row in projects_qs.values('status').annotate(c=Count('id')):
        overview_counts[row['status']] = row['c']
    projects_overview = {status_labels[k]: v for k, v in overview_counts.items()}
    projects_overview_json = json.dumps({
        'labels': list(projects_overview.keys()),
        'data': list(projects_overview.values()),
    })

    # ----- Income vs expense (area chart, last up to 12 months) -----
    snapshots = list(
        FinancialSnapshot.objects.filter(tenant=tenant).order_by('period')[:12]
    )
    income_expense = {
        'labels': [s.period for s in snapshots],
        'income': [float(s.income) for s in snapshots],
        'expense': [float(s.expense) for s in snapshots],
    }
    income_expense_json = json.dumps(income_expense)

    # ----- My tasks -----
    my_tasks = tasks_qs.filter(assignee=request.user).exclude(status='done')[:6]
    if not my_tasks:
        my_tasks = tasks_qs.exclude(status='done')[:6]

    # ----- My meetings (upcoming) -----
    my_meetings = Meeting.objects.filter(
        tenant=tenant, scheduled_for__gte=timezone.now()
    ).order_by('scheduled_for')[:5]

    # ----- Invoice overview (horizontal bars) -----
    invoice_status_map = [
        ('overdue', 'Overdue'),
        ('draft', 'Draft'),
        ('sent', 'Sent / Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
    ]
    sums = {
        row['status']: row['amount'] or Decimal('0')
        for row in project_invoices_qs.values('status').annotate(amount=Sum('total'))
    }
    invoice_overview_rows = []
    max_amount = Decimal('0')
    for key, label in invoice_status_map:
        amount = sums.get(key, Decimal('0'))
        max_amount = max(max_amount, amount)
        invoice_overview_rows.append({'key': key, 'label': label, 'amount': amount})
    invoice_overview = {
        'rows': invoice_overview_rows,
        'max': float(max_amount) if max_amount else 1.0,
    }

    # ----- Open tickets -----
    open_tickets = tickets_qs.filter(status__in=['open', 'in_progress'])[:6]

    context = {
        'page_title': 'Dashboard',
        'kpis': kpis,
        'projects_overview': projects_overview,
        'projects_overview_json': projects_overview_json,
        'income_expense': income_expense,
        'income_expense_json': income_expense_json,
        'my_tasks': my_tasks,
        'my_meetings': my_meetings,
        'invoice_overview': invoice_overview,
        'open_tickets': open_tickets,
        'recent_projects': projects_qs.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/index.html', context)
