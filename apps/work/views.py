"""Task & Work Management views: full CRUD for work items, priority scores,
board columns, board cards, and work dependencies. All tenant-scoped and
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
    BoardCardForm,
    BoardColumnForm,
    PriorityScoreForm,
    WorkDependencyForm,
    WorkItemForm,
)
from .models import (
    BoardCard,
    BoardColumn,
    PriorityScore,
    WorkDependency,
    WorkItem,
)


# ---------------------------------------------------------------------------
# Work items
# ---------------------------------------------------------------------------
@login_required
def workitem_list(request):
    qs = WorkItem.objects.filter(tenant=request.tenant).select_related(
        'project', 'assignee', 'reporter',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    item_type = request.GET.get('item_type', '').strip()
    if item_type:
        qs = qs.filter(item_type=item_type)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'work/workitem_list.html', {
        'page_title': 'Work Items',
        'page_obj': page_obj,
        'workitems': page_obj.object_list,
        'status_choices': WorkItem.STATUS_CHOICES,
        'type_choices': WorkItem.ITEM_TYPE_CHOICES,
        'priority_choices': WorkItem.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def workitem_detail(request, pk):
    obj = get_object_or_404(WorkItem, pk=pk, tenant=request.tenant)
    return render(request, 'work/workitem_detail.html', {
        'workitem': obj, 'page_title': str(obj),
    })


@login_required
def workitem_create(request):
    form = WorkItemForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'WorkItem', str(obj))
        messages.success(request, f'Work item "{obj.title}" created.')
        return redirect('work:workitem_detail', pk=obj.pk)
    return render(request, 'work/workitem_form.html', {
        'form': form, 'page_title': 'Create Work Item',
    })


@login_required
def workitem_edit(request, pk):
    obj = get_object_or_404(WorkItem, pk=pk, tenant=request.tenant)
    form = WorkItemForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'WorkItem', str(obj))
        messages.success(request, f'Work item "{obj.title}" updated.')
        return redirect('work:workitem_detail', pk=obj.pk)
    return render(request, 'work/workitem_form.html', {
        'form': form, 'workitem': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def workitem_delete(request, pk):
    obj = get_object_or_404(WorkItem, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'WorkItem', label)
        messages.success(request, 'Work item deleted.')
        return redirect('work:workitem_list')
    return redirect('work:workitem_list')


# ---------------------------------------------------------------------------
# Priority scores
# ---------------------------------------------------------------------------
@login_required
def priorityscore_list(request):
    qs = PriorityScore.objects.filter(tenant=request.tenant).select_related(
        'work_item', 'scored_by',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(work_item__number__icontains=q) | Q(work_item__title__icontains=q)
            | Q(rationale__icontains=q)
        )
    method = request.GET.get('method', '').strip()
    if method:
        qs = qs.filter(method=method)
    urgency = request.GET.get('urgency', '').strip()
    if urgency:
        qs = qs.filter(urgency=urgency)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'work/priorityscore_list.html', {
        'page_title': 'Priority Scores',
        'page_obj': page_obj,
        'priority_scores': page_obj.object_list,
        'method_choices': PriorityScore.METHOD_CHOICES,
        'urgency_choices': PriorityScore.URGENCY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def priorityscore_detail(request, pk):
    obj = get_object_or_404(PriorityScore, pk=pk, tenant=request.tenant)
    return render(request, 'work/priorityscore_detail.html', {
        'priorityscore': obj, 'page_title': str(obj),
    })


@login_required
def priorityscore_create(request):
    form = PriorityScoreForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'PriorityScore', str(obj))
        messages.success(request, 'Priority score created.')
        return redirect('work:priorityscore_detail', pk=obj.pk)
    return render(request, 'work/priorityscore_form.html', {
        'form': form, 'page_title': 'Create Priority Score',
    })


@login_required
def priorityscore_edit(request, pk):
    obj = get_object_or_404(PriorityScore, pk=pk, tenant=request.tenant)
    form = PriorityScoreForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'PriorityScore', str(obj))
        messages.success(request, 'Priority score updated.')
        return redirect('work:priorityscore_detail', pk=obj.pk)
    return render(request, 'work/priorityscore_form.html', {
        'form': form, 'priorityscore': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def priorityscore_delete(request, pk):
    obj = get_object_or_404(PriorityScore, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'PriorityScore', label)
        messages.success(request, 'Priority score deleted.')
        return redirect('work:priorityscore_list')
    return redirect('work:priorityscore_list')


# ---------------------------------------------------------------------------
# Board columns
# ---------------------------------------------------------------------------
@login_required
def boardcolumn_list(request):
    qs = BoardColumn.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    column_type = request.GET.get('column_type', '').strip()
    if column_type:
        qs = qs.filter(column_type=column_type)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'work/boardcolumn_list.html', {
        'page_title': 'Board Columns',
        'page_obj': page_obj,
        'board_columns': page_obj.object_list,
        'column_type_choices': BoardColumn.COLUMN_TYPE_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def boardcolumn_detail(request, pk):
    obj = get_object_or_404(BoardColumn, pk=pk, tenant=request.tenant)
    return render(request, 'work/boardcolumn_detail.html', {
        'boardcolumn': obj, 'page_title': str(obj),
    })


@login_required
def boardcolumn_create(request):
    form = BoardColumnForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'BoardColumn', str(obj))
        messages.success(request, f'Board column "{obj.name}" created.')
        return redirect('work:boardcolumn_detail', pk=obj.pk)
    return render(request, 'work/boardcolumn_form.html', {
        'form': form, 'page_title': 'Create Board Column',
    })


@login_required
def boardcolumn_edit(request, pk):
    obj = get_object_or_404(BoardColumn, pk=pk, tenant=request.tenant)
    form = BoardColumnForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'BoardColumn', str(obj))
        messages.success(request, f'Board column "{obj.name}" updated.')
        return redirect('work:boardcolumn_detail', pk=obj.pk)
    return render(request, 'work/boardcolumn_form.html', {
        'form': form, 'boardcolumn': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def boardcolumn_delete(request, pk):
    obj = get_object_or_404(BoardColumn, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'BoardColumn', label)
        messages.success(request, 'Board column deleted.')
        return redirect('work:boardcolumn_list')
    return redirect('work:boardcolumn_list')


# ---------------------------------------------------------------------------
# Board cards
# ---------------------------------------------------------------------------
@login_required
def boardcard_list(request):
    qs = BoardCard.objects.filter(tenant=request.tenant).select_related(
        'work_item', 'column',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q))
    column_id = request.GET.get('column', '').strip()
    if column_id.isdigit():
        qs = qs.filter(column_id=column_id)
    blocked = request.GET.get('blocked', '').strip()
    if blocked == 'yes':
        qs = qs.filter(is_blocked=True)
    elif blocked == 'no':
        qs = qs.filter(is_blocked=False)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'work/boardcard_list.html', {
        'page_title': 'Board Cards',
        'page_obj': page_obj,
        'board_cards': page_obj.object_list,
        'board_columns': BoardColumn.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def boardcard_detail(request, pk):
    obj = get_object_or_404(BoardCard, pk=pk, tenant=request.tenant)
    return render(request, 'work/boardcard_detail.html', {
        'boardcard': obj, 'page_title': str(obj),
    })


@login_required
def boardcard_create(request):
    form = BoardCardForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'BoardCard', str(obj))
        messages.success(request, f'Board card "{obj.title}" created.')
        return redirect('work:boardcard_detail', pk=obj.pk)
    return render(request, 'work/boardcard_form.html', {
        'form': form, 'page_title': 'Create Board Card',
    })


@login_required
def boardcard_edit(request, pk):
    obj = get_object_or_404(BoardCard, pk=pk, tenant=request.tenant)
    form = BoardCardForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'BoardCard', str(obj))
        messages.success(request, f'Board card "{obj.title}" updated.')
        return redirect('work:boardcard_detail', pk=obj.pk)
    return render(request, 'work/boardcard_form.html', {
        'form': form, 'boardcard': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def boardcard_delete(request, pk):
    obj = get_object_or_404(BoardCard, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'BoardCard', label)
        messages.success(request, 'Board card deleted.')
        return redirect('work:boardcard_list')
    return redirect('work:boardcard_list')


# ---------------------------------------------------------------------------
# Work dependencies
# ---------------------------------------------------------------------------
@login_required
def workdependency_list(request):
    qs = WorkDependency.objects.filter(tenant=request.tenant).select_related(
        'work_item', 'depends_on',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(work_item__title__icontains=q) | Q(depends_on__title__icontains=q)
            | Q(notes__icontains=q)
        )
    dependency_type = request.GET.get('dependency_type', '').strip()
    if dependency_type:
        qs = qs.filter(dependency_type=dependency_type)
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'work/workdependency_list.html', {
        'page_title': 'Work Dependencies',
        'page_obj': page_obj,
        'dependencies': page_obj.object_list,
        'dep_type_choices': WorkDependency.DEP_TYPE_CHOICES,
        'status_choices': WorkDependency.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def workdependency_detail(request, pk):
    obj = get_object_or_404(WorkDependency, pk=pk, tenant=request.tenant)
    return render(request, 'work/workdependency_detail.html', {
        'workdependency': obj, 'page_title': str(obj),
    })


@login_required
def workdependency_create(request):
    form = WorkDependencyForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'WorkDependency', str(obj))
        messages.success(request, 'Work dependency created.')
        return redirect('work:workdependency_detail', pk=obj.pk)
    return render(request, 'work/workdependency_form.html', {
        'form': form, 'page_title': 'Create Work Dependency',
    })


@login_required
def workdependency_edit(request, pk):
    obj = get_object_or_404(WorkDependency, pk=pk, tenant=request.tenant)
    form = WorkDependencyForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'WorkDependency', str(obj))
        messages.success(request, 'Work dependency updated.')
        return redirect('work:workdependency_detail', pk=obj.pk)
    return render(request, 'work/workdependency_form.html', {
        'form': form, 'workdependency': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def workdependency_delete(request, pk):
    obj = get_object_or_404(WorkDependency, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'WorkDependency', label)
        messages.success(request, 'Work dependency deleted.')
        return redirect('work:workdependency_list')
    return redirect('work:workdependency_list')
