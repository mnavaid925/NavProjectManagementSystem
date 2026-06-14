"""Projects workspace views: full CRUD for projects, tasks, meetings, tickets, invoices."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.core.utils import log_action

from .forms import (
    MeetingForm,
    ProjectForm,
    ProjectInvoiceForm,
    TaskForm,
    TicketForm,
)
from .models import Meeting, Project, ProjectInvoice, Task, Ticket


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
@login_required
def project_list(request):
    qs = Project.objects.filter(tenant=request.tenant).select_related('owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q) | Q(client_name__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'projects/project_list.html', {
        'page_title': 'Projects',
        'page_obj': page_obj,
        'projects': page_obj.object_list,
        'status_choices': Project.STATUS_CHOICES,
        'priority_choices': Project.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, tenant=request.tenant)
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': project.tasks.all()[:20],
        'tickets': project.tickets.all()[:10],
        'invoices': project.invoices.all()[:10],
        'page_title': project.name,
    })


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.tenant = request.tenant
        project.save()
        log_action(request, 'create', 'Project', project.name)
        messages.success(request, f'Project "{project.name}" created.')
        return redirect('projects:project_detail', pk=project.pk)
    return render(request, 'projects/project_form.html', {'form': form, 'page_title': 'Create Project'})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, tenant=request.tenant)
    form = ProjectForm(request.POST or None, instance=project, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'Project', project.name)
        messages.success(request, f'Project "{project.name}" updated.')
        return redirect('projects:project_detail', pk=project.pk)
    return render(request, 'projects/project_form.html', {
        'form': form, 'project': project, 'page_title': f'Edit {project.name}',
    })


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        name = project.name
        project.delete()
        log_action(request, 'delete', 'Project', name)
        messages.success(request, f'Project "{name}" deleted.')
        return redirect('projects:project_list')
    return redirect('projects:project_list')


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
@login_required
def task_list(request):
    qs = Task.objects.filter(tenant=request.tenant).select_related('project', 'assignee')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id:
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'projects/task_list.html', {
        'page_title': 'Tasks',
        'page_obj': page_obj,
        'tasks': page_obj.object_list,
        'status_choices': Task.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, tenant=request.tenant)
    return render(request, 'projects/task_detail.html', {'task': task, 'page_title': task.title})


@login_required
def task_create(request):
    form = TaskForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.tenant = request.tenant
        _sync_task_done(task)
        task.save()
        log_action(request, 'create', 'Task', task.title)
        messages.success(request, f'Task "{task.title}" created.')
        return redirect('projects:task_list')
    return render(request, 'projects/task_form.html', {'form': form, 'page_title': 'Create Task'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, tenant=request.tenant)
    form = TaskForm(request.POST or None, instance=task, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        _sync_task_done(task)
        task.save()
        log_action(request, 'update', 'Task', task.title)
        messages.success(request, f'Task "{task.title}" updated.')
        return redirect('projects:task_list')
    return render(request, 'projects/task_form.html', {
        'form': form, 'task': task, 'page_title': f'Edit {task.title}',
    })


def _sync_task_done(task):
    """Keep is_done / status / completed_at consistent."""
    if task.status == 'done':
        task.is_done = True
        if not task.completed_at:
            task.completed_at = timezone.now()
    else:
        task.is_done = False
        task.completed_at = None


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        title = task.title
        task.delete()
        log_action(request, 'delete', 'Task', title)
        messages.success(request, f'Task "{title}" deleted.')
        return redirect('projects:task_list')
    return redirect('projects:task_list')


# ---------------------------------------------------------------------------
# Meetings
# ---------------------------------------------------------------------------
@login_required
def meeting_list(request):
    qs = Meeting.objects.filter(tenant=request.tenant).select_related('organizer')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(location__icontains=q))
    mtype = request.GET.get('meeting_type', '').strip()
    if mtype:
        qs = qs.filter(meeting_type=mtype)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'projects/meeting_list.html', {
        'page_title': 'Meetings',
        'page_obj': page_obj,
        'meetings': page_obj.object_list,
        'meeting_type_choices': Meeting.MEETING_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    return render(request, 'projects/meeting_detail.html', {
        'meeting': meeting, 'page_title': meeting.title,
    })


@login_required
def meeting_create(request):
    form = MeetingForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        meeting = form.save(commit=False)
        meeting.tenant = request.tenant
        meeting.save()
        form.save_m2m()
        log_action(request, 'create', 'Meeting', meeting.title)
        messages.success(request, f'Meeting "{meeting.title}" scheduled.')
        return redirect('projects:meeting_list')
    return render(request, 'projects/meeting_form.html', {'form': form, 'page_title': 'Schedule Meeting'})


@login_required
def meeting_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    form = MeetingForm(request.POST or None, instance=meeting, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'Meeting', meeting.title)
        messages.success(request, f'Meeting "{meeting.title}" updated.')
        return redirect('projects:meeting_list')
    return render(request, 'projects/meeting_form.html', {
        'form': form, 'meeting': meeting, 'page_title': f'Edit {meeting.title}',
    })


@login_required
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        title = meeting.title
        meeting.delete()
        log_action(request, 'delete', 'Meeting', title)
        messages.success(request, f'Meeting "{title}" deleted.')
        return redirect('projects:meeting_list')
    return redirect('projects:meeting_list')


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------
@login_required
def ticket_list(request):
    qs = Ticket.objects.filter(tenant=request.tenant).select_related('project', 'assignee', 'requester')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(subject__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'projects/ticket_list.html', {
        'page_title': 'Tickets',
        'page_obj': page_obj,
        'tickets': page_obj.object_list,
        'status_choices': Ticket.STATUS_CHOICES,
        'category_choices': Ticket.CATEGORY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, tenant=request.tenant)
    return render(request, 'projects/ticket_detail.html', {
        'ticket': ticket, 'page_title': ticket.subject,
    })


@login_required
def ticket_create(request):
    form = TicketForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.tenant = request.tenant
        if not ticket.requester_id:
            ticket.requester = request.user
        ticket.save()
        log_action(request, 'create', 'Ticket', ticket.subject)
        messages.success(request, f'Ticket "{ticket.subject}" created.')
        return redirect('projects:ticket_detail', pk=ticket.pk)
    return render(request, 'projects/ticket_form.html', {'form': form, 'page_title': 'Create Ticket'})


@login_required
def ticket_edit(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, tenant=request.tenant)
    form = TicketForm(request.POST or None, instance=ticket, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'Ticket', ticket.subject)
        messages.success(request, f'Ticket "{ticket.subject}" updated.')
        return redirect('projects:ticket_detail', pk=ticket.pk)
    return render(request, 'projects/ticket_form.html', {
        'form': form, 'ticket': ticket, 'page_title': f'Edit {ticket.subject}',
    })


@login_required
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        subject = ticket.subject
        ticket.delete()
        log_action(request, 'delete', 'Ticket', subject)
        messages.success(request, f'Ticket "{subject}" deleted.')
        return redirect('projects:ticket_list')
    return redirect('projects:ticket_list')


# ---------------------------------------------------------------------------
# Project invoices
# ---------------------------------------------------------------------------
@login_required
def invoice_list(request):
    qs = ProjectInvoice.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(client_name__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'projects/invoice_list.html', {
        'page_title': 'Project Invoices',
        'page_obj': page_obj,
        'invoices': page_obj.object_list,
        'status_choices': ProjectInvoice.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(ProjectInvoice, pk=pk, tenant=request.tenant)
    return render(request, 'projects/invoice_detail.html', {
        'invoice': invoice, 'page_title': invoice.number,
    })


@login_required
def invoice_create(request):
    form = ProjectInvoiceForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        invoice = form.save(commit=False)
        invoice.tenant = request.tenant
        invoice.total = (invoice.amount or 0) + (invoice.tax or 0)
        invoice.save()
        log_action(request, 'create', 'ProjectInvoice', invoice.number)
        messages.success(request, f'Invoice {invoice.number} created.')
        return redirect('projects:invoice_detail', pk=invoice.pk)
    return render(request, 'projects/invoice_form.html', {'form': form, 'page_title': 'Create Invoice'})


@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(ProjectInvoice, pk=pk, tenant=request.tenant)
    form = ProjectInvoiceForm(request.POST or None, instance=invoice, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.total = (obj.amount or 0) + (obj.tax or 0)
        obj.save()
        log_action(request, 'update', 'ProjectInvoice', invoice.number)
        messages.success(request, f'Invoice {invoice.number} updated.')
        return redirect('projects:invoice_detail', pk=invoice.pk)
    return render(request, 'projects/invoice_form.html', {
        'form': form, 'invoice': invoice, 'page_title': f'Edit {invoice.number}',
    })


@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(ProjectInvoice, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        number = invoice.number
        invoice.delete()
        log_action(request, 'delete', 'ProjectInvoice', number)
        messages.success(request, f'Invoice {number} deleted.')
        return redirect('projects:invoice_list')
    return redirect('projects:invoice_list')
