"""Reporting & Business Intelligence views: full CRUD for report definitions,
report runs, dashboard widgets, executive packs, and data exports. All
tenant-scoped and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action

from .forms import (
    DashboardWidgetForm,
    DataExportForm,
    ExecutivePackForm,
    ReportDefinitionForm,
    ReportRunForm,
)
from .models import (
    DashboardWidget,
    DataExport,
    ExecutivePack,
    ReportDefinition,
    ReportRun,
)


# ---------------------------------------------------------------------------
# Report definitions
# ---------------------------------------------------------------------------
@login_required
def reportdefinition_list(request):
    qs = ReportDefinition.objects.filter(tenant=request.tenant).select_related(
        'project', 'owner',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'reporting/reportdefinition_list.html', {
        'page_title': 'Report Definitions',
        'page_obj': page_obj,
        'report_definitions': page_obj.object_list,
        'status_choices': ReportDefinition.STATUS_CHOICES,
        'category_choices': ReportDefinition.CATEGORY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def reportdefinition_detail(request, pk):
    obj = get_object_or_404(ReportDefinition, pk=pk, tenant=request.tenant)
    return render(request, 'reporting/reportdefinition_detail.html', {
        'reportdefinition': obj, 'page_title': str(obj),
    })


@login_required
def reportdefinition_create(request):
    form = ReportDefinitionForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ReportDefinition', str(obj))
        messages.success(request, f'Report definition "{obj.name}" created.')
        return redirect('reporting:reportdefinition_detail', pk=obj.pk)
    return render(request, 'reporting/reportdefinition_form.html', {
        'form': form, 'page_title': 'Create Report Definition',
    })


@login_required
def reportdefinition_edit(request, pk):
    obj = get_object_or_404(ReportDefinition, pk=pk, tenant=request.tenant)
    form = ReportDefinitionForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ReportDefinition', str(obj))
        messages.success(request, f'Report definition "{obj.name}" updated.')
        return redirect('reporting:reportdefinition_detail', pk=obj.pk)
    return render(request, 'reporting/reportdefinition_form.html', {
        'form': form, 'reportdefinition': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def reportdefinition_delete(request, pk):
    obj = get_object_or_404(ReportDefinition, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ReportDefinition', label)
        messages.success(request, 'Report definition deleted.')
        return redirect('reporting:reportdefinition_list')
    return redirect('reporting:reportdefinition_list')


# ---------------------------------------------------------------------------
# Report runs
# ---------------------------------------------------------------------------
@login_required
def reportrun_list(request):
    qs = ReportRun.objects.filter(tenant=request.tenant).select_related(
        'report', 'run_by',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(notes__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    format_value = request.GET.get('format', '').strip()
    if format_value:
        qs = qs.filter(format=format_value)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'reporting/reportrun_list.html', {
        'page_title': 'Report Runs',
        'page_obj': page_obj,
        'report_runs': page_obj.object_list,
        'status_choices': ReportRun.STATUS_CHOICES,
        'format_choices': ReportRun.FORMAT_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def reportrun_detail(request, pk):
    obj = get_object_or_404(ReportRun, pk=pk, tenant=request.tenant)
    return render(request, 'reporting/reportrun_detail.html', {
        'reportrun': obj, 'page_title': str(obj),
    })


@login_required
def reportrun_create(request):
    form = ReportRunForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ReportRun', str(obj))
        messages.success(request, f'Report run "{obj.number}" created.')
        return redirect('reporting:reportrun_detail', pk=obj.pk)
    return render(request, 'reporting/reportrun_form.html', {
        'form': form, 'page_title': 'Create Report Run',
    })


@login_required
def reportrun_edit(request, pk):
    obj = get_object_or_404(ReportRun, pk=pk, tenant=request.tenant)
    form = ReportRunForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ReportRun', str(obj))
        messages.success(request, f'Report run "{obj.number}" updated.')
        return redirect('reporting:reportrun_detail', pk=obj.pk)
    return render(request, 'reporting/reportrun_form.html', {
        'form': form, 'reportrun': obj, 'page_title': f'Edit {obj.number}',
    })


@login_required
def reportrun_delete(request, pk):
    obj = get_object_or_404(ReportRun, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ReportRun', label)
        messages.success(request, 'Report run deleted.')
        return redirect('reporting:reportrun_list')
    return redirect('reporting:reportrun_list')


# ---------------------------------------------------------------------------
# Dashboard widgets
# ---------------------------------------------------------------------------
@login_required
def dashboardwidget_list(request):
    qs = DashboardWidget.objects.filter(tenant=request.tenant).select_related('owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q) | Q(metric__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    widget_type = request.GET.get('widget_type', '').strip()
    if widget_type:
        qs = qs.filter(widget_type=widget_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'reporting/dashboardwidget_list.html', {
        'page_title': 'Dashboard Widgets',
        'page_obj': page_obj,
        'dashboard_widgets': page_obj.object_list,
        'status_choices': DashboardWidget.STATUS_CHOICES,
        'widget_type_choices': DashboardWidget.WIDGET_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def dashboardwidget_detail(request, pk):
    obj = get_object_or_404(DashboardWidget, pk=pk, tenant=request.tenant)
    return render(request, 'reporting/dashboardwidget_detail.html', {
        'dashboardwidget': obj, 'page_title': str(obj),
    })


@login_required
def dashboardwidget_create(request):
    form = DashboardWidgetForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'DashboardWidget', str(obj))
        messages.success(request, f'Dashboard widget "{obj.title}" created.')
        return redirect('reporting:dashboardwidget_detail', pk=obj.pk)
    return render(request, 'reporting/dashboardwidget_form.html', {
        'form': form, 'page_title': 'Create Dashboard Widget',
    })


@login_required
def dashboardwidget_edit(request, pk):
    obj = get_object_or_404(DashboardWidget, pk=pk, tenant=request.tenant)
    form = DashboardWidgetForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'DashboardWidget', str(obj))
        messages.success(request, f'Dashboard widget "{obj.title}" updated.')
        return redirect('reporting:dashboardwidget_detail', pk=obj.pk)
    return render(request, 'reporting/dashboardwidget_form.html', {
        'form': form, 'dashboardwidget': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def dashboardwidget_delete(request, pk):
    obj = get_object_or_404(DashboardWidget, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'DashboardWidget', label)
        messages.success(request, 'Dashboard widget deleted.')
        return redirect('reporting:dashboardwidget_list')
    return redirect('reporting:dashboardwidget_list')


# ---------------------------------------------------------------------------
# Executive packs
# ---------------------------------------------------------------------------
@login_required
def executivepack_list(request):
    qs = ExecutivePack.objects.filter(tenant=request.tenant).select_related(
        'project', 'prepared_by',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q) | Q(summary__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    rag_status = request.GET.get('rag_status', '').strip()
    if rag_status:
        qs = qs.filter(rag_status=rag_status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'reporting/executivepack_list.html', {
        'page_title': 'Executive Packs',
        'page_obj': page_obj,
        'executive_packs': page_obj.object_list,
        'status_choices': ExecutivePack.STATUS_CHOICES,
        'rag_status_choices': ExecutivePack.RAG_STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def executivepack_detail(request, pk):
    obj = get_object_or_404(ExecutivePack, pk=pk, tenant=request.tenant)
    return render(request, 'reporting/executivepack_detail.html', {
        'executivepack': obj, 'page_title': str(obj),
    })


@login_required
def executivepack_create(request):
    form = ExecutivePackForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ExecutivePack', str(obj))
        messages.success(request, f'Executive pack "{obj.title}" created.')
        return redirect('reporting:executivepack_detail', pk=obj.pk)
    return render(request, 'reporting/executivepack_form.html', {
        'form': form, 'page_title': 'Create Executive Pack',
    })


@login_required
def executivepack_edit(request, pk):
    obj = get_object_or_404(ExecutivePack, pk=pk, tenant=request.tenant)
    form = ExecutivePackForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ExecutivePack', str(obj))
        messages.success(request, f'Executive pack "{obj.title}" updated.')
        return redirect('reporting:executivepack_detail', pk=obj.pk)
    return render(request, 'reporting/executivepack_form.html', {
        'form': form, 'executivepack': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def executivepack_delete(request, pk):
    obj = get_object_or_404(ExecutivePack, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ExecutivePack', label)
        messages.success(request, 'Executive pack deleted.')
        return redirect('reporting:executivepack_list')
    return redirect('reporting:executivepack_list')


# ---------------------------------------------------------------------------
# Data exports
# ---------------------------------------------------------------------------
@login_required
def dataexport_list(request):
    qs = DataExport.objects.filter(tenant=request.tenant).select_related('requested_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(destination__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    export_type = request.GET.get('export_type', '').strip()
    if export_type:
        qs = qs.filter(export_type=export_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'reporting/dataexport_list.html', {
        'page_title': 'Data Exports',
        'page_obj': page_obj,
        'data_exports': page_obj.object_list,
        'status_choices': DataExport.STATUS_CHOICES,
        'export_type_choices': DataExport.EXPORT_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def dataexport_detail(request, pk):
    obj = get_object_or_404(DataExport, pk=pk, tenant=request.tenant)
    return render(request, 'reporting/dataexport_detail.html', {
        'dataexport': obj, 'page_title': str(obj),
    })


@login_required
def dataexport_create(request):
    form = DataExportForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'DataExport', str(obj))
        messages.success(request, f'Data export "{obj.name}" created.')
        return redirect('reporting:dataexport_detail', pk=obj.pk)
    return render(request, 'reporting/dataexport_form.html', {
        'form': form, 'page_title': 'Create Data Export',
    })


@login_required
def dataexport_edit(request, pk):
    obj = get_object_or_404(DataExport, pk=pk, tenant=request.tenant)
    form = DataExportForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'DataExport', str(obj))
        messages.success(request, f'Data export "{obj.name}" updated.')
        return redirect('reporting:dataexport_detail', pk=obj.pk)
    return render(request, 'reporting/dataexport_form.html', {
        'form': form, 'dataexport': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def dataexport_delete(request, pk):
    obj = get_object_or_404(DataExport, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'DataExport', label)
        messages.success(request, 'Data export deleted.')
        return redirect('reporting:dataexport_list')
    return redirect('reporting:dataexport_list')
