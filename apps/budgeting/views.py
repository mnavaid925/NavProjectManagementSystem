"""Cost & Budget Management views: full CRUD for budgets, control accounts,
expenses, cost forecasts, and budget changes. All tenant-scoped + @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    BudgetChangeForm,
    BudgetForm,
    ControlAccountForm,
    CostForecastForm,
    ExpenseForm,
)
from .models import (
    Budget,
    BudgetChange,
    ControlAccount,
    CostForecast,
    Expense,
)


# ---------------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------------
@login_required
def budget_list(request):
    qs = Budget.objects.filter(tenant=request.tenant).select_related('project', 'owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(number__icontains=q) | Q(fiscal_year__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'budgeting/budget_list.html', {
        'page_title': 'Budgets',
        'page_obj': page_obj,
        'budgets': page_obj.object_list,
        'status_choices': Budget.STATUS_CHOICES,
        'category_choices': Budget.CATEGORY_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def budget_detail(request, pk):
    obj = get_object_or_404(Budget, pk=pk, tenant=request.tenant)
    return render(request, 'budgeting/budget_detail.html', {
        'budget': obj, 'page_title': str(obj),
    })


@login_required
def budget_create(request):
    form = BudgetForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Budget', str(obj))
        messages.success(request, f'Budget "{obj.name}" created.')
        return redirect('budgeting:budget_detail', pk=obj.pk)
    return render(request, 'budgeting/budget_form.html', {
        'form': form, 'page_title': 'Create Budget',
    })


@login_required
def budget_edit(request, pk):
    obj = get_object_or_404(Budget, pk=pk, tenant=request.tenant)
    form = BudgetForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Budget', str(obj))
        messages.success(request, f'Budget "{obj.name}" updated.')
        return redirect('budgeting:budget_detail', pk=obj.pk)
    return render(request, 'budgeting/budget_form.html', {
        'form': form, 'budget': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def budget_delete(request, pk):
    obj = get_object_or_404(Budget, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Budget', label)
        messages.success(request, 'Budget deleted.')
        return redirect('budgeting:budget_list')
    return redirect('budgeting:budget_list')


# ---------------------------------------------------------------------------
# Control accounts
# ---------------------------------------------------------------------------
@login_required
def controlaccount_list(request):
    qs = ControlAccount.objects.filter(tenant=request.tenant).select_related(
        'project', 'budget', 'manager',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'budgeting/controlaccount_list.html', {
        'page_title': 'Control Accounts',
        'page_obj': page_obj,
        'control_accounts': page_obj.object_list,
        'status_choices': ControlAccount.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def controlaccount_detail(request, pk):
    obj = get_object_or_404(ControlAccount, pk=pk, tenant=request.tenant)
    return render(request, 'budgeting/controlaccount_detail.html', {
        'controlaccount': obj, 'page_title': str(obj),
    })


@login_required
def controlaccount_create(request):
    form = ControlAccountForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ControlAccount', str(obj))
        messages.success(request, f'Control account "{obj.name}" created.')
        return redirect('budgeting:controlaccount_detail', pk=obj.pk)
    return render(request, 'budgeting/controlaccount_form.html', {
        'form': form, 'page_title': 'Create Control Account',
    })


@login_required
def controlaccount_edit(request, pk):
    obj = get_object_or_404(ControlAccount, pk=pk, tenant=request.tenant)
    form = ControlAccountForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ControlAccount', str(obj))
        messages.success(request, f'Control account "{obj.name}" updated.')
        return redirect('budgeting:controlaccount_detail', pk=obj.pk)
    return render(request, 'budgeting/controlaccount_form.html', {
        'form': form, 'controlaccount': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def controlaccount_delete(request, pk):
    obj = get_object_or_404(ControlAccount, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ControlAccount', label)
        messages.success(request, 'Control account deleted.')
        return redirect('budgeting:controlaccount_list')
    return redirect('budgeting:controlaccount_list')


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
@login_required
def expense_list(request):
    qs = Expense.objects.filter(tenant=request.tenant).select_related(
        'project', 'control_account', 'submitted_by',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(description__icontains=q) | Q(vendor__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    expense_type = request.GET.get('expense_type', '').strip()
    if expense_type:
        qs = qs.filter(expense_type=expense_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'budgeting/expense_list.html', {
        'page_title': 'Expenses',
        'page_obj': page_obj,
        'expenses': page_obj.object_list,
        'status_choices': Expense.STATUS_CHOICES,
        'category_choices': Expense.CATEGORY_CHOICES,
        'type_choices': Expense.TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def expense_detail(request, pk):
    obj = get_object_or_404(Expense, pk=pk, tenant=request.tenant)
    return render(request, 'budgeting/expense_detail.html', {
        'expense': obj, 'page_title': str(obj),
    })


@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Expense', str(obj))
        messages.success(request, f'Expense "{obj.description}" created.')
        return redirect('budgeting:expense_detail', pk=obj.pk)
    return render(request, 'budgeting/expense_form.html', {
        'form': form, 'page_title': 'Create Expense',
    })


@login_required
def expense_edit(request, pk):
    obj = get_object_or_404(Expense, pk=pk, tenant=request.tenant)
    form = ExpenseForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Expense', str(obj))
        messages.success(request, f'Expense "{obj.description}" updated.')
        return redirect('budgeting:expense_detail', pk=obj.pk)
    return render(request, 'budgeting/expense_form.html', {
        'form': form, 'expense': obj, 'page_title': f'Edit {obj.description}',
    })


@login_required
def expense_delete(request, pk):
    obj = get_object_or_404(Expense, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Expense', label)
        messages.success(request, 'Expense deleted.')
        return redirect('budgeting:expense_list')
    return redirect('budgeting:expense_list')


# ---------------------------------------------------------------------------
# Cost forecasts
# ---------------------------------------------------------------------------
@login_required
def forecast_list(request):
    qs = CostForecast.objects.filter(tenant=request.tenant).select_related('project', 'budget')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(period__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    method = request.GET.get('method', '').strip()
    if method:
        qs = qs.filter(method=method)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'budgeting/forecast_list.html', {
        'page_title': 'Cost Forecasts',
        'page_obj': page_obj,
        'forecasts': page_obj.object_list,
        'status_choices': CostForecast.STATUS_CHOICES,
        'method_choices': CostForecast.METHOD_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def forecast_detail(request, pk):
    obj = get_object_or_404(CostForecast, pk=pk, tenant=request.tenant)
    return render(request, 'budgeting/forecast_detail.html', {
        'forecast': obj, 'page_title': str(obj),
    })


@login_required
def forecast_create(request):
    form = CostForecastForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'CostForecast', str(obj))
        messages.success(request, f'Forecast "{obj.name}" created.')
        return redirect('budgeting:forecast_detail', pk=obj.pk)
    return render(request, 'budgeting/forecast_form.html', {
        'form': form, 'page_title': 'Create Cost Forecast',
    })


@login_required
def forecast_edit(request, pk):
    obj = get_object_or_404(CostForecast, pk=pk, tenant=request.tenant)
    form = CostForecastForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'CostForecast', str(obj))
        messages.success(request, f'Forecast "{obj.name}" updated.')
        return redirect('budgeting:forecast_detail', pk=obj.pk)
    return render(request, 'budgeting/forecast_form.html', {
        'form': form, 'forecast': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def forecast_delete(request, pk):
    obj = get_object_or_404(CostForecast, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'CostForecast', label)
        messages.success(request, 'Forecast deleted.')
        return redirect('budgeting:forecast_list')
    return redirect('budgeting:forecast_list')


# ---------------------------------------------------------------------------
# Budget changes
# ---------------------------------------------------------------------------
@login_required
def change_list(request):
    qs = BudgetChange.objects.filter(tenant=request.tenant).select_related('budget', 'requested_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    change_type = request.GET.get('change_type', '').strip()
    if change_type:
        qs = qs.filter(change_type=change_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'budgeting/change_list.html', {
        'page_title': 'Budget Changes',
        'page_obj': page_obj,
        'changes': page_obj.object_list,
        'status_choices': BudgetChange.STATUS_CHOICES,
        'type_choices': BudgetChange.TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def change_detail(request, pk):
    obj = get_object_or_404(BudgetChange, pk=pk, tenant=request.tenant)
    return render(request, 'budgeting/change_detail.html', {
        'change': obj, 'page_title': str(obj),
    })


@login_required
def change_create(request):
    form = BudgetChangeForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'BudgetChange', str(obj))
        messages.success(request, f'Budget change "{obj.title}" created.')
        return redirect('budgeting:change_detail', pk=obj.pk)
    return render(request, 'budgeting/change_form.html', {
        'form': form, 'page_title': 'Create Budget Change',
    })


@login_required
def change_edit(request, pk):
    obj = get_object_or_404(BudgetChange, pk=pk, tenant=request.tenant)
    form = BudgetChangeForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'BudgetChange', str(obj))
        messages.success(request, f'Budget change "{obj.title}" updated.')
        return redirect('budgeting:change_detail', pk=obj.pk)
    return render(request, 'budgeting/change_form.html', {
        'form': form, 'change': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def change_delete(request, pk):
    obj = get_object_or_404(BudgetChange, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'BudgetChange', label)
        messages.success(request, 'Budget change deleted.')
        return redirect('budgeting:change_list')
    return redirect('budgeting:change_list')
