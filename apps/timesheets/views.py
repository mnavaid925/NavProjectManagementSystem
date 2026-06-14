"""Time & Attendance Tracking views: full CRUD for timesheets, timesheet
lines, timesheet approvals, leave records, and utilization snapshots. All
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
    LeaveRecordForm,
    TimesheetApprovalForm,
    TimesheetForm,
    TimesheetLineForm,
    UtilizationSnapshotForm,
)
from .models import (
    LeaveRecord,
    Timesheet,
    TimesheetApproval,
    TimesheetLine,
    UtilizationSnapshot,
)


# ---------------------------------------------------------------------------
# Timesheets
# ---------------------------------------------------------------------------
@login_required
def timesheet_list(request):
    qs = Timesheet.objects.filter(tenant=request.tenant).select_related('owner', 'project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(notes__icontains=q)
            | Q(owner__first_name__icontains=q) | Q(owner__last_name__icontains=q)
            | Q(owner__username__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'timesheets/timesheet_list.html', {
        'page_title': 'Timesheets',
        'page_obj': page_obj,
        'timesheets': page_obj.object_list,
        'status_choices': Timesheet.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def timesheet_detail(request, pk):
    obj = get_object_or_404(Timesheet, pk=pk, tenant=request.tenant)
    return render(request, 'timesheets/timesheet_detail.html', {
        'timesheet': obj, 'page_title': str(obj),
    })


@login_required
def timesheet_create(request):
    form = TimesheetForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Timesheet', str(obj))
        messages.success(request, f'Timesheet "{obj.number}" created.')
        return redirect('timesheets:timesheet_detail', pk=obj.pk)
    return render(request, 'timesheets/timesheet_form.html', {
        'form': form, 'page_title': 'Create Timesheet',
    })


@login_required
def timesheet_edit(request, pk):
    obj = get_object_or_404(Timesheet, pk=pk, tenant=request.tenant)
    form = TimesheetForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Timesheet', str(obj))
        messages.success(request, f'Timesheet "{obj.number}" updated.')
        return redirect('timesheets:timesheet_detail', pk=obj.pk)
    return render(request, 'timesheets/timesheet_form.html', {
        'form': form, 'timesheet': obj, 'page_title': f'Edit {obj.number}',
    })


@login_required
def timesheet_delete(request, pk):
    obj = get_object_or_404(Timesheet, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Timesheet', label)
        messages.success(request, 'Timesheet deleted.')
        return redirect('timesheets:timesheet_list')
    return redirect('timesheets:timesheet_list')


# ---------------------------------------------------------------------------
# Timesheet lines
# ---------------------------------------------------------------------------
@login_required
def timesheetline_list(request):
    qs = TimesheetLine.objects.filter(tenant=request.tenant).select_related(
        'timesheet', 'timesheet__owner', 'project',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(description__icontains=q) | Q(activity__icontains=q)
            | Q(timesheet__number__icontains=q)
        )
    activity = request.GET.get('activity', '').strip()
    if activity:
        qs = qs.filter(activity=activity)
    b = request.GET.get('billable', '').strip()
    if b == 'yes':
        qs = qs.filter(is_billable=True)
    elif b == 'no':
        qs = qs.filter(is_billable=False)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'timesheets/timesheetline_list.html', {
        'page_title': 'Timesheet Lines',
        'page_obj': page_obj,
        'timesheet_lines': page_obj.object_list,
        'activity_choices': TimesheetLine.ACTIVITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def timesheetline_detail(request, pk):
    obj = get_object_or_404(TimesheetLine, pk=pk, tenant=request.tenant)
    return render(request, 'timesheets/timesheetline_detail.html', {
        'timesheetline': obj, 'page_title': str(obj),
    })


@login_required
def timesheetline_create(request):
    form = TimesheetLineForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'TimesheetLine', str(obj))
        messages.success(request, 'Timesheet line created.')
        return redirect('timesheets:timesheetline_detail', pk=obj.pk)
    return render(request, 'timesheets/timesheetline_form.html', {
        'form': form, 'page_title': 'Create Timesheet Line',
    })


@login_required
def timesheetline_edit(request, pk):
    obj = get_object_or_404(TimesheetLine, pk=pk, tenant=request.tenant)
    form = TimesheetLineForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'TimesheetLine', str(obj))
        messages.success(request, 'Timesheet line updated.')
        return redirect('timesheets:timesheetline_detail', pk=obj.pk)
    return render(request, 'timesheets/timesheetline_form.html', {
        'form': form, 'timesheetline': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def timesheetline_delete(request, pk):
    obj = get_object_or_404(TimesheetLine, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'TimesheetLine', label)
        messages.success(request, 'Timesheet line deleted.')
        return redirect('timesheets:timesheetline_list')
    return redirect('timesheets:timesheetline_list')


# ---------------------------------------------------------------------------
# Timesheet approvals
# ---------------------------------------------------------------------------
@login_required
def timesheetapproval_list(request):
    qs = TimesheetApproval.objects.filter(tenant=request.tenant).select_related(
        'timesheet', 'timesheet__owner', 'approver',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(comments__icontains=q) | Q(timesheet__number__icontains=q)
        )
    decision = request.GET.get('decision', '').strip()
    if decision:
        qs = qs.filter(decision=decision)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'timesheets/timesheetapproval_list.html', {
        'page_title': 'Timesheet Approvals',
        'page_obj': page_obj,
        'approvals': page_obj.object_list,
        'decision_choices': TimesheetApproval.DECISION_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def timesheetapproval_detail(request, pk):
    obj = get_object_or_404(
        TimesheetApproval.objects.select_related('timesheet', 'timesheet__owner', 'approver'),
        pk=pk, tenant=request.tenant,
    )
    return render(request, 'timesheets/timesheetapproval_detail.html', {
        'timesheetapproval': obj, 'page_title': str(obj),
    })


@login_required
def timesheetapproval_create(request):
    form = TimesheetApprovalForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'TimesheetApproval', str(obj))
        messages.success(request, 'Timesheet approval created.')
        return redirect('timesheets:timesheetapproval_detail', pk=obj.pk)
    return render(request, 'timesheets/timesheetapproval_form.html', {
        'form': form, 'page_title': 'Create Timesheet Approval',
    })


@login_required
def timesheetapproval_edit(request, pk):
    obj = get_object_or_404(TimesheetApproval, pk=pk, tenant=request.tenant)
    form = TimesheetApprovalForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'TimesheetApproval', str(obj))
        messages.success(request, 'Timesheet approval updated.')
        return redirect('timesheets:timesheetapproval_detail', pk=obj.pk)
    return render(request, 'timesheets/timesheetapproval_form.html', {
        'form': form, 'timesheetapproval': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def timesheetapproval_delete(request, pk):
    obj = get_object_or_404(TimesheetApproval, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'TimesheetApproval', label)
        messages.success(request, 'Timesheet approval deleted.')
        return redirect('timesheets:timesheetapproval_list')
    return redirect('timesheets:timesheetapproval_list')


# ---------------------------------------------------------------------------
# Leave records
# ---------------------------------------------------------------------------
@login_required
def leaverecord_list(request):
    qs = LeaveRecord.objects.filter(tenant=request.tenant).select_related(
        'owner', 'approved_by',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(reason__icontains=q)
            | Q(owner__first_name__icontains=q) | Q(owner__last_name__icontains=q)
            | Q(owner__username__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    leave_type = request.GET.get('leave_type', '').strip()
    if leave_type:
        qs = qs.filter(leave_type=leave_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'timesheets/leaverecord_list.html', {
        'page_title': 'Leave Records',
        'page_obj': page_obj,
        'leave_records': page_obj.object_list,
        'status_choices': LeaveRecord.STATUS_CHOICES,
        'type_choices': LeaveRecord.LEAVE_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def leaverecord_detail(request, pk):
    obj = get_object_or_404(LeaveRecord, pk=pk, tenant=request.tenant)
    return render(request, 'timesheets/leaverecord_detail.html', {
        'leaverecord': obj, 'page_title': str(obj),
    })


@login_required
def leaverecord_create(request):
    form = LeaveRecordForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'LeaveRecord', str(obj))
        messages.success(request, f'Leave record "{obj.number}" created.')
        return redirect('timesheets:leaverecord_detail', pk=obj.pk)
    return render(request, 'timesheets/leaverecord_form.html', {
        'form': form, 'page_title': 'Create Leave Record',
    })


@login_required
def leaverecord_edit(request, pk):
    obj = get_object_or_404(LeaveRecord, pk=pk, tenant=request.tenant)
    form = LeaveRecordForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'LeaveRecord', str(obj))
        messages.success(request, f'Leave record "{obj.number}" updated.')
        return redirect('timesheets:leaverecord_detail', pk=obj.pk)
    return render(request, 'timesheets/leaverecord_form.html', {
        'form': form, 'leaverecord': obj, 'page_title': f'Edit {obj.number}',
    })


@login_required
def leaverecord_delete(request, pk):
    obj = get_object_or_404(LeaveRecord, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'LeaveRecord', label)
        messages.success(request, 'Leave record deleted.')
        return redirect('timesheets:leaverecord_list')
    return redirect('timesheets:leaverecord_list')


# ---------------------------------------------------------------------------
# Utilization snapshots
# ---------------------------------------------------------------------------
@login_required
def utilizationsnapshot_list(request):
    qs = UtilizationSnapshot.objects.filter(tenant=request.tenant).select_related(
        'owner', 'project',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(period__icontains=q)
            | Q(owner__first_name__icontains=q) | Q(owner__last_name__icontains=q)
            | Q(owner__username__icontains=q)
        )
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'timesheets/utilizationsnapshot_list.html', {
        'page_title': 'Utilization Snapshots',
        'page_obj': page_obj,
        'utilization_snapshots': page_obj.object_list,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def utilizationsnapshot_detail(request, pk):
    obj = get_object_or_404(UtilizationSnapshot, pk=pk, tenant=request.tenant)
    return render(request, 'timesheets/utilizationsnapshot_detail.html', {
        'utilizationsnapshot': obj, 'page_title': str(obj),
    })


@login_required
def utilizationsnapshot_create(request):
    form = UtilizationSnapshotForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'UtilizationSnapshot', str(obj))
        messages.success(request, 'Utilization snapshot created.')
        return redirect('timesheets:utilizationsnapshot_detail', pk=obj.pk)
    return render(request, 'timesheets/utilizationsnapshot_form.html', {
        'form': form, 'page_title': 'Create Utilization Snapshot',
    })


@login_required
def utilizationsnapshot_edit(request, pk):
    obj = get_object_or_404(UtilizationSnapshot, pk=pk, tenant=request.tenant)
    form = UtilizationSnapshotForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'UtilizationSnapshot', str(obj))
        messages.success(request, 'Utilization snapshot updated.')
        return redirect('timesheets:utilizationsnapshot_detail', pk=obj.pk)
    return render(request, 'timesheets/utilizationsnapshot_form.html', {
        'form': form, 'utilizationsnapshot': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def utilizationsnapshot_delete(request, pk):
    obj = get_object_or_404(UtilizationSnapshot, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'UtilizationSnapshot', label)
        messages.success(request, 'Utilization snapshot deleted.')
        return redirect('timesheets:utilizationsnapshot_list')
    return redirect('timesheets:utilizationsnapshot_list')
