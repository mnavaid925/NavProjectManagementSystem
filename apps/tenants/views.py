"""Module 0 - Tenant & Subscription Management views (tenant-scoped)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import AuditLog
from apps.core.utils import log_action

from .forms import (
    BrandingForm,
    InvoiceForm,
    PaymentMethodForm,
    PlanForm,
    TenantConfigForm,
)
from .models import (
    BrandingSettings,
    Invoice,
    PaymentMethod,
    Plan,
    Subscription,
    SystemAlert,
    UsageMetric,
)


# ---------------------------------------------------------------------------
# Onboarding wizard
# ---------------------------------------------------------------------------
@login_required
def onboarding(request):
    tenant = request.tenant
    if tenant is None:
        messages.warning(request, 'Log in as a tenant admin to view onboarding.')
        return render(request, 'tenants/onboarding.html', {'page_title': 'Tenant Onboarding'})

    form = TenantConfigForm(request.POST or None, instance=tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'Tenant', tenant.name, 'Onboarding configuration')
        messages.success(request, 'Organization configuration saved.')
        return redirect('tenants:onboarding')

    subscription_obj = getattr(tenant, 'subscription', None)
    branding_obj, _ = BrandingSettings.objects.get_or_create(tenant=tenant)
    context = {
        'page_title': 'Tenant Onboarding',
        'tenant': tenant,
        'form': form,
        'subscription': subscription_obj,
        'branding': branding_obj,
        'member_count': tenant.users.count(),
        'project_count': tenant.projects.count(),
    }
    return render(request, 'tenants/onboarding.html', context)


# ---------------------------------------------------------------------------
# Subscription & billing
# ---------------------------------------------------------------------------
@login_required
def subscription(request):
    tenant = request.tenant
    subscription_obj = getattr(tenant, 'subscription', None) if tenant else None

    if request.method == 'POST' and subscription_obj is not None:
        plan_id = request.POST.get('plan')
        cycle = request.POST.get('billing_cycle', subscription_obj.billing_cycle)
        new_plan = Plan.objects.filter(pk=plan_id, is_active=True).first()
        if new_plan:
            subscription_obj.plan = new_plan
            if cycle in ('monthly', 'yearly'):
                subscription_obj.billing_cycle = cycle
            if subscription_obj.status == Subscription.STATUS_TRIALING:
                subscription_obj.status = Subscription.STATUS_ACTIVE
            subscription_obj.save()
            log_action(request, 'change_plan', 'Subscription', new_plan.name)
            messages.success(request, f'Plan changed to {new_plan.name}.')
        return redirect('tenants:subscription')

    context = {
        'page_title': 'Subscription & Billing',
        'subscription': subscription_obj,
        'plans': Plan.objects.filter(is_active=True),
        'payment_methods': PaymentMethod.objects.filter(tenant=tenant) if tenant else PaymentMethod.objects.none(),
        'recent_invoices': Invoice.objects.filter(tenant=tenant)[:5] if tenant else Invoice.objects.none(),
    }
    return render(request, 'tenants/subscription.html', context)


# ---------------------------------------------------------------------------
# Plans (global catalog; edits restricted to staff / tenant admins)
# ---------------------------------------------------------------------------
def _can_manage_plans(user):
    return user.is_staff or getattr(user, 'is_tenant_admin', False)


@login_required
def plan_list(request):
    qs = Plan.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)
    status = request.GET.get('status', '').strip()
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tenants/plan_list.html', {
        'page_title': 'Subscription Plans',
        'page_obj': page_obj,
        'plans': page_obj.object_list,
        'status_options': [('active', 'Active'), ('inactive', 'Inactive')],
        'can_manage': _can_manage_plans(request.user),
        'total_count': paginator.count,
    })


@login_required
def plan_create(request):
    if not _can_manage_plans(request.user):
        messages.error(request, 'You do not have permission to manage plans.')
        return redirect('tenants:plan_list')
    form = PlanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        plan = form.save(commit=False)
        if not plan.slug:
            plan.slug = slugify(plan.name)
        plan.save()
        log_action(request, 'create', 'Plan', plan.name)
        messages.success(request, f'Plan "{plan.name}" created.')
        return redirect('tenants:plan_list')
    return render(request, 'tenants/plan_form.html', {'form': form, 'page_title': 'Create Plan'})


@login_required
def plan_edit(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if not _can_manage_plans(request.user):
        messages.error(request, 'You do not have permission to manage plans.')
        return redirect('tenants:plan_list')
    form = PlanForm(request.POST or None, instance=plan)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'Plan', plan.name)
        messages.success(request, f'Plan "{plan.name}" updated.')
        return redirect('tenants:plan_list')
    return render(request, 'tenants/plan_form.html', {
        'form': form, 'plan': plan, 'page_title': f'Edit {plan.name}',
    })


@login_required
def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == 'POST':
        if not _can_manage_plans(request.user):
            messages.error(request, 'You do not have permission to manage plans.')
            return redirect('tenants:plan_list')
        name = plan.name
        plan.delete()
        log_action(request, 'delete', 'Plan', name)
        messages.success(request, f'Plan "{name}" deleted.')
        return redirect('tenants:plan_list')
    return redirect('tenants:plan_list')


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------
@login_required
def invoice_list(request):
    qs = Invoice.objects.filter(tenant=request.tenant).select_related('subscription')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(notes__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tenants/invoice_list.html', {
        'page_title': 'Invoices',
        'page_obj': page_obj,
        'invoices': page_obj.object_list,
        'status_choices': Invoice.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, tenant=request.tenant)
    return render(request, 'tenants/invoice_detail.html', {
        'invoice': invoice, 'page_title': invoice.number,
    })


@login_required
def invoice_create(request):
    form = InvoiceForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        invoice = form.save(commit=False)
        invoice.tenant = request.tenant
        invoice.save()
        log_action(request, 'create', 'Invoice', invoice.number)
        messages.success(request, f'Invoice {invoice.number} created.')
        return redirect('tenants:invoice_detail', pk=invoice.pk)
    return render(request, 'tenants/invoice_form.html', {'form': form, 'page_title': 'Create Invoice'})


@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, tenant=request.tenant)
    form = InvoiceForm(request.POST or None, instance=invoice, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.total = (obj.amount or 0) + (obj.tax or 0)
        obj.save()
        log_action(request, 'update', 'Invoice', invoice.number)
        messages.success(request, f'Invoice {invoice.number} updated.')
        return redirect('tenants:invoice_detail', pk=invoice.pk)
    return render(request, 'tenants/invoice_form.html', {
        'form': form, 'invoice': invoice, 'page_title': f'Edit {invoice.number}',
    })


@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        number = invoice.number
        invoice.delete()
        log_action(request, 'delete', 'Invoice', number)
        messages.success(request, f'Invoice {number} deleted.')
        return redirect('tenants:invoice_list')
    return redirect('tenants:invoice_list')


@login_required
def invoice_mark_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        invoice.status = Invoice.STATUS_PAID
        invoice.paid_at = timezone.now().date()
        invoice.save(update_fields=['status', 'paid_at', 'updated_at'])
        log_action(request, 'mark_paid', 'Invoice', invoice.number)
        messages.success(request, f'Invoice {invoice.number} marked as paid.')
    return redirect('tenants:invoice_detail', pk=invoice.pk)


# ---------------------------------------------------------------------------
# Payment methods
# ---------------------------------------------------------------------------
@login_required
def payment_method_list(request):
    qs = PaymentMethod.objects.filter(tenant=request.tenant)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tenants/payment_method_list.html', {
        'page_title': 'Payment Methods',
        'page_obj': page_obj,
        'payment_methods': page_obj.object_list,
        'total_count': paginator.count,
    })


@login_required
def payment_method_create(request):
    form = PaymentMethodForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        pm = form.save(commit=False)
        pm.tenant = request.tenant
        pm.save()
        if pm.is_default:
            PaymentMethod.objects.filter(tenant=request.tenant).exclude(pk=pm.pk).update(is_default=False)
        log_action(request, 'create', 'PaymentMethod', str(pm))
        messages.success(request, 'Payment method added.')
        return redirect('tenants:payment_method_list')
    return render(request, 'tenants/payment_method_form.html', {'form': form, 'page_title': 'Add Payment Method'})


@login_required
def payment_method_edit(request, pk):
    pm = get_object_or_404(PaymentMethod, pk=pk, tenant=request.tenant)
    form = PaymentMethodForm(request.POST or None, instance=pm)
    if request.method == 'POST' and form.is_valid():
        pm = form.save()
        if pm.is_default:
            PaymentMethod.objects.filter(tenant=request.tenant).exclude(pk=pm.pk).update(is_default=False)
        log_action(request, 'update', 'PaymentMethod', str(pm))
        messages.success(request, 'Payment method updated.')
        return redirect('tenants:payment_method_list')
    return render(request, 'tenants/payment_method_form.html', {
        'form': form, 'payment_method': pm, 'page_title': 'Edit Payment Method',
    })


@login_required
def payment_method_delete(request, pk):
    pm = get_object_or_404(PaymentMethod, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(pm)
        pm.delete()
        log_action(request, 'delete', 'PaymentMethod', label)
        messages.success(request, 'Payment method removed.')
        return redirect('tenants:payment_method_list')
    return redirect('tenants:payment_method_list')


@login_required
def payment_method_set_default(request, pk):
    pm = get_object_or_404(PaymentMethod, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        PaymentMethod.objects.filter(tenant=request.tenant).update(is_default=False)
        pm.is_default = True
        pm.save(update_fields=['is_default'])
        log_action(request, 'set_default', 'PaymentMethod', str(pm))
        messages.success(request, 'Default payment method updated.')
    return redirect('tenants:payment_method_list')


# ---------------------------------------------------------------------------
# Isolation & security
# ---------------------------------------------------------------------------
@login_required
def isolation_security(request):
    tenant = request.tenant
    security_alerts = SystemAlert.objects.filter(
        tenant=tenant, category='security'
    ) if tenant else SystemAlert.objects.none()
    recent_audit = AuditLog.objects.filter(tenant=tenant)[:10] if tenant else AuditLog.objects.none()
    context = {
        'page_title': 'Tenant Isolation & Security',
        'tenant': tenant,
        'security_alerts': security_alerts,
        'recent_audit': recent_audit,
        'audit_count': AuditLog.objects.filter(tenant=tenant).count() if tenant else 0,
        'isolation_model': 'Row-level (shared schema)',
        'encryption_at_rest': True,
        'encryption_in_transit': True,
    }
    return render(request, 'tenants/isolation_security.html', context)


# ---------------------------------------------------------------------------
# Branding
# ---------------------------------------------------------------------------
@login_required
def branding(request):
    tenant = request.tenant
    if tenant is None:
        messages.warning(request, 'Log in as a tenant admin to manage branding.')
        return render(request, 'tenants/branding.html', {'page_title': 'Custom Branding'})
    branding_obj, _ = BrandingSettings.objects.get_or_create(tenant=tenant)
    form = BrandingForm(request.POST or None, request.FILES or None, instance=branding_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'BrandingSettings', tenant.name)
        messages.success(request, 'Branding settings saved.')
        return redirect('tenants:branding')
    return render(request, 'tenants/branding.html', {
        'page_title': 'Custom Branding', 'form': form, 'branding': branding_obj, 'tenant': tenant,
    })


# ---------------------------------------------------------------------------
# Health monitoring
# ---------------------------------------------------------------------------
@login_required
def health(request):
    tenant = request.tenant
    usage_metrics = UsageMetric.objects.filter(tenant=tenant) if tenant else UsageMetric.objects.none()
    alerts = SystemAlert.objects.filter(tenant=tenant) if tenant else SystemAlert.objects.none()
    context = {
        'page_title': 'Tenant Health Monitoring',
        'usage_metrics': usage_metrics,
        'alerts': alerts,
        'open_alerts': alerts.filter(is_resolved=False) if tenant else SystemAlert.objects.none(),
        'open_alert_count': alerts.filter(is_resolved=False).count() if tenant else 0,
    }
    return render(request, 'tenants/health.html', context)


@login_required
def alert_resolve(request, pk):
    alert = get_object_or_404(SystemAlert, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save(update_fields=['is_resolved', 'resolved_at', 'updated_at'])
        log_action(request, 'resolve', 'SystemAlert', alert.title)
        messages.success(request, 'Alert resolved.')
    return redirect('tenants:health')


@login_required
def usage_list(request):
    qs = UsageMetric.objects.filter(tenant=request.tenant)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tenants/usage_list.html', {
        'page_title': 'Usage Metrics',
        'page_obj': page_obj,
        'usage_metrics': page_obj.object_list,
        'total_count': paginator.count,
    })
