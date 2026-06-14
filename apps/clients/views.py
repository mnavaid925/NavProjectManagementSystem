"""Client & External Collaboration views: full CRUD for client access records,
client feedback, SOW contracts, external vendors, and client invoices. All
tenant-scoped and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    ClientAccessForm,
    ClientFeedbackForm,
    ClientInvoiceForm,
    ExternalVendorForm,
    SOWContractForm,
)
from .models import (
    ClientAccess,
    ClientFeedback,
    ClientInvoice,
    ExternalVendor,
    SOWContract,
)


# ---------------------------------------------------------------------------
# Client access records
# ---------------------------------------------------------------------------
@login_required
def access_list(request):
    qs = ClientAccess.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(client_name__icontains=q) | Q(contact_name__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    access_level = request.GET.get('access_level', '').strip()
    if access_level:
        qs = qs.filter(access_level=access_level)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'clients/access_list.html', {
        'page_title': 'Client Access',
        'page_obj': page_obj,
        'access_records': page_obj.object_list,
        'status_choices': ClientAccess.STATUS_CHOICES,
        'access_level_choices': ClientAccess.ACCESS_LEVEL_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def access_detail(request, pk):
    obj = get_object_or_404(ClientAccess, pk=pk, tenant=request.tenant)
    return render(request, 'clients/access_detail.html', {
        'access': obj, 'page_title': str(obj),
    })


@login_required
def access_create(request):
    form = ClientAccessForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ClientAccess', str(obj))
        messages.success(request, f'Client access "{obj.client_name}" created.')
        return redirect('clients:access_detail', pk=obj.pk)
    return render(request, 'clients/access_form.html', {
        'form': form, 'page_title': 'Create Client Access',
    })


@login_required
def access_edit(request, pk):
    obj = get_object_or_404(ClientAccess, pk=pk, tenant=request.tenant)
    form = ClientAccessForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ClientAccess', str(obj))
        messages.success(request, f'Client access "{obj.client_name}" updated.')
        return redirect('clients:access_detail', pk=obj.pk)
    return render(request, 'clients/access_form.html', {
        'form': form, 'access': obj, 'page_title': f'Edit {obj.client_name}',
    })


@login_required
def access_delete(request, pk):
    obj = get_object_or_404(ClientAccess, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ClientAccess', label)
        messages.success(request, 'Client access deleted.')
        return redirect('clients:access_list')
    return redirect('clients:access_list')


# ---------------------------------------------------------------------------
# Client feedback
# ---------------------------------------------------------------------------
@login_required
def feedback_list(request):
    qs = ClientFeedback.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(subject__icontains=q) | Q(client_name__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    feedback_type = request.GET.get('feedback_type', '').strip()
    if feedback_type:
        qs = qs.filter(feedback_type=feedback_type)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'clients/feedback_list.html', {
        'page_title': 'Client Feedback',
        'page_obj': page_obj,
        'feedback_items': page_obj.object_list,
        'status_choices': ClientFeedback.STATUS_CHOICES,
        'feedback_type_choices': ClientFeedback.FEEDBACK_TYPE_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def feedback_detail(request, pk):
    obj = get_object_or_404(ClientFeedback, pk=pk, tenant=request.tenant)
    return render(request, 'clients/feedback_detail.html', {
        'feedback': obj, 'page_title': str(obj),
    })


@login_required
def feedback_create(request):
    form = ClientFeedbackForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ClientFeedback', str(obj))
        messages.success(request, f'Client feedback "{obj.subject}" created.')
        return redirect('clients:feedback_detail', pk=obj.pk)
    return render(request, 'clients/feedback_form.html', {
        'form': form, 'page_title': 'Create Client Feedback',
    })


@login_required
def feedback_edit(request, pk):
    obj = get_object_or_404(ClientFeedback, pk=pk, tenant=request.tenant)
    form = ClientFeedbackForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ClientFeedback', str(obj))
        messages.success(request, f'Client feedback "{obj.subject}" updated.')
        return redirect('clients:feedback_detail', pk=obj.pk)
    return render(request, 'clients/feedback_form.html', {
        'form': form, 'feedback': obj, 'page_title': f'Edit {obj.subject}',
    })


@login_required
def feedback_delete(request, pk):
    obj = get_object_or_404(ClientFeedback, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ClientFeedback', label)
        messages.success(request, 'Client feedback deleted.')
        return redirect('clients:feedback_list')
    return redirect('clients:feedback_list')


# ---------------------------------------------------------------------------
# SOW contracts
# ---------------------------------------------------------------------------
@login_required
def contract_list(request):
    qs = SOWContract.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q) | Q(client_name__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    contract_type = request.GET.get('contract_type', '').strip()
    if contract_type:
        qs = qs.filter(contract_type=contract_type)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'clients/contract_list.html', {
        'page_title': 'SOW Contracts',
        'page_obj': page_obj,
        'contracts': page_obj.object_list,
        'status_choices': SOWContract.STATUS_CHOICES,
        'contract_type_choices': SOWContract.CONTRACT_TYPE_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def contract_detail(request, pk):
    obj = get_object_or_404(SOWContract, pk=pk, tenant=request.tenant)
    return render(request, 'clients/contract_detail.html', {
        'contract': obj, 'page_title': str(obj),
    })


@login_required
def contract_create(request):
    form = SOWContractForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'SOWContract', str(obj))
        messages.success(request, f'Contract "{obj.title}" created.')
        return redirect('clients:contract_detail', pk=obj.pk)
    return render(request, 'clients/contract_form.html', {
        'form': form, 'page_title': 'Create SOW Contract',
    })


@login_required
def contract_edit(request, pk):
    obj = get_object_or_404(SOWContract, pk=pk, tenant=request.tenant)
    form = SOWContractForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'SOWContract', str(obj))
        messages.success(request, f'Contract "{obj.title}" updated.')
        return redirect('clients:contract_detail', pk=obj.pk)
    return render(request, 'clients/contract_form.html', {
        'form': form, 'contract': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def contract_delete(request, pk):
    obj = get_object_or_404(SOWContract, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'SOWContract', label)
        messages.success(request, 'Contract deleted.')
        return redirect('clients:contract_list')
    return redirect('clients:contract_list')


# ---------------------------------------------------------------------------
# External vendors
# ---------------------------------------------------------------------------
@login_required
def vendor_list(request):
    qs = ExternalVendor.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(contact_name__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    service_type = request.GET.get('service_type', '').strip()
    if service_type:
        qs = qs.filter(service_type=service_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'clients/vendor_list.html', {
        'page_title': 'External Vendors',
        'page_obj': page_obj,
        'vendors': page_obj.object_list,
        'status_choices': ExternalVendor.STATUS_CHOICES,
        'service_type_choices': ExternalVendor.SERVICE_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def vendor_detail(request, pk):
    obj = get_object_or_404(ExternalVendor, pk=pk, tenant=request.tenant)
    return render(request, 'clients/vendor_detail.html', {
        'vendor': obj, 'page_title': str(obj),
    })


@login_required
def vendor_create(request):
    form = ExternalVendorForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ExternalVendor', str(obj))
        messages.success(request, f'Vendor "{obj.name}" created.')
        return redirect('clients:vendor_detail', pk=obj.pk)
    return render(request, 'clients/vendor_form.html', {
        'form': form, 'page_title': 'Create External Vendor',
    })


@login_required
def vendor_edit(request, pk):
    obj = get_object_or_404(ExternalVendor, pk=pk, tenant=request.tenant)
    form = ExternalVendorForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ExternalVendor', str(obj))
        messages.success(request, f'Vendor "{obj.name}" updated.')
        return redirect('clients:vendor_detail', pk=obj.pk)
    return render(request, 'clients/vendor_form.html', {
        'form': form, 'vendor': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def vendor_delete(request, pk):
    obj = get_object_or_404(ExternalVendor, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ExternalVendor', label)
        messages.success(request, 'Vendor deleted.')
        return redirect('clients:vendor_list')
    return redirect('clients:vendor_list')


# ---------------------------------------------------------------------------
# Client invoices
# ---------------------------------------------------------------------------
@login_required
def invoice_list(request):
    qs = ClientInvoice.objects.filter(tenant=request.tenant).select_related('project', 'contract')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(client_name__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    billing_type = request.GET.get('billing_type', '').strip()
    if billing_type:
        qs = qs.filter(billing_type=billing_type)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'clients/invoice_list.html', {
        'page_title': 'Client Invoices',
        'page_obj': page_obj,
        'invoices': page_obj.object_list,
        'status_choices': ClientInvoice.STATUS_CHOICES,
        'billing_type_choices': ClientInvoice.BILLING_TYPE_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def invoice_detail(request, pk):
    obj = get_object_or_404(ClientInvoice, pk=pk, tenant=request.tenant)
    return render(request, 'clients/invoice_detail.html', {
        'invoice': obj, 'page_title': str(obj),
    })


@login_required
def invoice_create(request):
    form = ClientInvoiceForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ClientInvoice', str(obj))
        messages.success(request, f'Invoice "{obj.client_name}" created.')
        return redirect('clients:invoice_detail', pk=obj.pk)
    return render(request, 'clients/invoice_form.html', {
        'form': form, 'page_title': 'Create Client Invoice',
    })


@login_required
def invoice_edit(request, pk):
    obj = get_object_or_404(ClientInvoice, pk=pk, tenant=request.tenant)
    form = ClientInvoiceForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ClientInvoice', str(obj))
        messages.success(request, f'Invoice "{obj.client_name}" updated.')
        return redirect('clients:invoice_detail', pk=obj.pk)
    return render(request, 'clients/invoice_form.html', {
        'form': form, 'invoice': obj, 'page_title': f'Edit {obj.client_name}',
    })


@login_required
def invoice_delete(request, pk):
    obj = get_object_or_404(ClientInvoice, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ClientInvoice', label)
        messages.success(request, 'Invoice deleted.')
        return redirect('clients:invoice_list')
    return redirect('clients:invoice_list')
