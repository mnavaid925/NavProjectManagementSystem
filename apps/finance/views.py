"""Financial & Billing Management views: full CRUD for cost centers, invoices,
payments, budget-vs-actual records, and currency rates. All tenant-scoped and
@login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    BudgetActualForm,
    CostCenterForm,
    CurrencyRateForm,
    FinanceInvoiceForm,
    PaymentForm,
)
from .models import (
    BudgetActual,
    CostCenter,
    CurrencyRate,
    FinanceInvoice,
    Payment,
)


# ---------------------------------------------------------------------------
# Cost centers
# ---------------------------------------------------------------------------
@login_required
def costcenter_list(request):
    qs = CostCenter.objects.filter(tenant=request.tenant).select_related('manager')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(code__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    cost_center_type = request.GET.get('cost_center_type', '').strip()
    if cost_center_type:
        qs = qs.filter(cost_center_type=cost_center_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'finance/costcenter_list.html', {
        'page_title': 'Cost Centers',
        'page_obj': page_obj,
        'cost_centers': page_obj.object_list,
        'status_choices': CostCenter.STATUS_CHOICES,
        'type_choices': CostCenter.COST_CENTER_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def costcenter_detail(request, pk):
    obj = get_object_or_404(CostCenter, pk=pk, tenant=request.tenant)
    return render(request, 'finance/costcenter_detail.html', {
        'costcenter': obj, 'page_title': str(obj),
    })


@login_required
def costcenter_create(request):
    form = CostCenterForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'CostCenter', str(obj))
        messages.success(request, f'Cost center "{obj.name}" created.')
        return redirect('finance:costcenter_detail', pk=obj.pk)
    return render(request, 'finance/costcenter_form.html', {
        'form': form, 'page_title': 'Create Cost Center',
    })


@login_required
def costcenter_edit(request, pk):
    obj = get_object_or_404(CostCenter, pk=pk, tenant=request.tenant)
    form = CostCenterForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'CostCenter', str(obj))
        messages.success(request, f'Cost center "{obj.name}" updated.')
        return redirect('finance:costcenter_detail', pk=obj.pk)
    return render(request, 'finance/costcenter_form.html', {
        'form': form, 'costcenter': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def costcenter_delete(request, pk):
    obj = get_object_or_404(CostCenter, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'CostCenter', label)
        messages.success(request, 'Cost center deleted.')
        return redirect('finance:costcenter_list')
    return redirect('finance:costcenter_list')


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------
@login_required
def invoice_list(request):
    qs = FinanceInvoice.objects.filter(tenant=request.tenant).select_related(
        'project', 'cost_center',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(client_name__icontains=q) | Q(notes__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'finance/invoice_list.html', {
        'page_title': 'Invoices',
        'page_obj': page_obj,
        'invoices': page_obj.object_list,
        'status_choices': FinanceInvoice.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def invoice_detail(request, pk):
    obj = get_object_or_404(FinanceInvoice, pk=pk, tenant=request.tenant)
    return render(request, 'finance/invoice_detail.html', {
        'invoice': obj, 'page_title': str(obj),
    })


@login_required
def invoice_create(request):
    form = FinanceInvoiceForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'FinanceInvoice', str(obj))
        messages.success(request, f'Invoice for "{obj.client_name}" created.')
        return redirect('finance:invoice_detail', pk=obj.pk)
    return render(request, 'finance/invoice_form.html', {
        'form': form, 'page_title': 'Create Invoice',
    })


@login_required
def invoice_edit(request, pk):
    obj = get_object_or_404(FinanceInvoice, pk=pk, tenant=request.tenant)
    form = FinanceInvoiceForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'FinanceInvoice', str(obj))
        messages.success(request, f'Invoice for "{obj.client_name}" updated.')
        return redirect('finance:invoice_detail', pk=obj.pk)
    return render(request, 'finance/invoice_form.html', {
        'form': form, 'invoice': obj, 'page_title': f'Edit {obj.client_name}',
    })


@login_required
def invoice_delete(request, pk):
    obj = get_object_or_404(FinanceInvoice, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'FinanceInvoice', label)
        messages.success(request, 'Invoice deleted.')
        return redirect('finance:invoice_list')
    return redirect('finance:invoice_list')


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------
@login_required
def payment_list(request):
    qs = Payment.objects.filter(tenant=request.tenant).select_related('invoice')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(reference__icontains=q)
            | Q(invoice__number__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    method = request.GET.get('method', '').strip()
    if method:
        qs = qs.filter(method=method)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'finance/payment_list.html', {
        'page_title': 'Payments',
        'page_obj': page_obj,
        'payments': page_obj.object_list,
        'status_choices': Payment.STATUS_CHOICES,
        'method_choices': Payment.METHOD_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def payment_detail(request, pk):
    obj = get_object_or_404(Payment, pk=pk, tenant=request.tenant)
    return render(request, 'finance/payment_detail.html', {
        'payment': obj, 'page_title': str(obj),
    })


@login_required
def payment_create(request):
    form = PaymentForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Payment', str(obj))
        messages.success(request, 'Payment created.')
        return redirect('finance:payment_detail', pk=obj.pk)
    return render(request, 'finance/payment_form.html', {
        'form': form, 'page_title': 'Create Payment',
    })


@login_required
def payment_edit(request, pk):
    obj = get_object_or_404(Payment, pk=pk, tenant=request.tenant)
    form = PaymentForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Payment', str(obj))
        messages.success(request, 'Payment updated.')
        return redirect('finance:payment_detail', pk=obj.pk)
    return render(request, 'finance/payment_form.html', {
        'form': form, 'payment': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def payment_delete(request, pk):
    obj = get_object_or_404(Payment, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Payment', label)
        messages.success(request, 'Payment deleted.')
        return redirect('finance:payment_list')
    return redirect('finance:payment_list')


# ---------------------------------------------------------------------------
# Budget vs actual
# ---------------------------------------------------------------------------
@login_required
def budgetactual_list(request):
    qs = BudgetActual.objects.filter(tenant=request.tenant).select_related(
        'project', 'cost_center',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(period__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'finance/budgetactual_list.html', {
        'page_title': 'Budget vs Actual',
        'page_obj': page_obj,
        'budget_actuals': page_obj.object_list,
        'status_choices': BudgetActual.STATUS_CHOICES,
        'category_choices': BudgetActual.CATEGORY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def budgetactual_detail(request, pk):
    obj = get_object_or_404(BudgetActual, pk=pk, tenant=request.tenant)
    return render(request, 'finance/budgetactual_detail.html', {
        'budgetactual': obj, 'page_title': str(obj),
    })


@login_required
def budgetactual_create(request):
    form = BudgetActualForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'BudgetActual', str(obj))
        messages.success(request, f'Budget vs actual "{obj.period}" created.')
        return redirect('finance:budgetactual_detail', pk=obj.pk)
    return render(request, 'finance/budgetactual_form.html', {
        'form': form, 'page_title': 'Create Budget vs Actual',
    })


@login_required
def budgetactual_edit(request, pk):
    obj = get_object_or_404(BudgetActual, pk=pk, tenant=request.tenant)
    form = BudgetActualForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'BudgetActual', str(obj))
        messages.success(request, f'Budget vs actual "{obj.period}" updated.')
        return redirect('finance:budgetactual_detail', pk=obj.pk)
    return render(request, 'finance/budgetactual_form.html', {
        'form': form, 'budgetactual': obj, 'page_title': f'Edit {obj.period}',
    })


@login_required
def budgetactual_delete(request, pk):
    obj = get_object_or_404(BudgetActual, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'BudgetActual', label)
        messages.success(request, 'Budget vs actual deleted.')
        return redirect('finance:budgetactual_list')
    return redirect('finance:budgetactual_list')


# ---------------------------------------------------------------------------
# Currency rates
# ---------------------------------------------------------------------------
@login_required
def currencyrate_list(request):
    qs = CurrencyRate.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(base_currency__icontains=q) | Q(target_currency__icontains=q)
            | Q(source__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'finance/currencyrate_list.html', {
        'page_title': 'Currency Rates',
        'page_obj': page_obj,
        'currency_rates': page_obj.object_list,
        'status_choices': CurrencyRate.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def currencyrate_detail(request, pk):
    obj = get_object_or_404(CurrencyRate, pk=pk, tenant=request.tenant)
    return render(request, 'finance/currencyrate_detail.html', {
        'currencyrate': obj, 'page_title': str(obj),
    })


@login_required
def currencyrate_create(request):
    form = CurrencyRateForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'CurrencyRate', str(obj))
        messages.success(request, 'Currency rate created.')
        return redirect('finance:currencyrate_detail', pk=obj.pk)
    return render(request, 'finance/currencyrate_form.html', {
        'form': form, 'page_title': 'Create Currency Rate',
    })


@login_required
def currencyrate_edit(request, pk):
    obj = get_object_or_404(CurrencyRate, pk=pk, tenant=request.tenant)
    form = CurrencyRateForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'CurrencyRate', str(obj))
        messages.success(request, 'Currency rate updated.')
        return redirect('finance:currencyrate_detail', pk=obj.pk)
    return render(request, 'finance/currencyrate_form.html', {
        'form': form, 'currencyrate': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def currencyrate_delete(request, pk):
    obj = get_object_or_404(CurrencyRate, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'CurrencyRate', label)
        messages.success(request, 'Currency rate deleted.')
        return redirect('finance:currencyrate_list')
    return redirect('finance:currencyrate_list')
