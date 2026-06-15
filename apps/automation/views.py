"""Workflow & Automation views: full CRUD for workflow definitions, approval
rules, notification rules, recurring rules, and automation hooks. All
tenant-scoped and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action

from .forms import (
    ApprovalRuleForm,
    AutomationHookForm,
    NotificationRuleForm,
    RecurringRuleForm,
    WorkflowDefinitionForm,
)
from .models import (
    ApprovalRule,
    AutomationHook,
    NotificationRule,
    RecurringRule,
    WorkflowDefinition,
)


# ---------------------------------------------------------------------------
# Workflow definitions
# ---------------------------------------------------------------------------
@login_required
def workflowdefinition_list(request):
    qs = WorkflowDefinition.objects.filter(tenant=request.tenant).select_related(
        'project', 'owner',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(entity_type__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    trigger_event = request.GET.get('trigger_event', '').strip()
    if trigger_event:
        qs = qs.filter(trigger_event=trigger_event)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'automation/workflowdefinition_list.html', {
        'page_title': 'Workflows',
        'page_obj': page_obj,
        'workflow_definitions': page_obj.object_list,
        'status_choices': WorkflowDefinition.STATUS_CHOICES,
        'trigger_event_choices': WorkflowDefinition.TRIGGER_EVENT_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def workflowdefinition_detail(request, pk):
    obj = get_object_or_404(WorkflowDefinition, pk=pk, tenant=request.tenant)
    return render(request, 'automation/workflowdefinition_detail.html', {
        'workflowdefinition': obj, 'page_title': str(obj),
    })


@login_required
def workflowdefinition_create(request):
    form = WorkflowDefinitionForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'WorkflowDefinition', str(obj))
        messages.success(request, f'Workflow "{obj.name}" created.')
        return redirect('automation:workflowdefinition_detail', pk=obj.pk)
    return render(request, 'automation/workflowdefinition_form.html', {
        'form': form, 'page_title': 'Create Workflow',
    })


@login_required
def workflowdefinition_edit(request, pk):
    obj = get_object_or_404(WorkflowDefinition, pk=pk, tenant=request.tenant)
    form = WorkflowDefinitionForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'WorkflowDefinition', str(obj))
        messages.success(request, f'Workflow "{obj.name}" updated.')
        return redirect('automation:workflowdefinition_detail', pk=obj.pk)
    return render(request, 'automation/workflowdefinition_form.html', {
        'form': form, 'workflowdefinition': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def workflowdefinition_delete(request, pk):
    obj = get_object_or_404(WorkflowDefinition, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'WorkflowDefinition', label)
        messages.success(request, 'Workflow deleted.')
        return redirect('automation:workflowdefinition_list')
    return redirect('automation:workflowdefinition_list')


# ---------------------------------------------------------------------------
# Approval rules
# ---------------------------------------------------------------------------
@login_required
def approvalrule_list(request):
    qs = ApprovalRule.objects.filter(tenant=request.tenant).select_related('approver')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(entity_type__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'automation/approvalrule_list.html', {
        'page_title': 'Approval Rules',
        'page_obj': page_obj,
        'approval_rules': page_obj.object_list,
        'status_choices': ApprovalRule.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def approvalrule_detail(request, pk):
    obj = get_object_or_404(ApprovalRule, pk=pk, tenant=request.tenant)
    return render(request, 'automation/approvalrule_detail.html', {
        'approvalrule': obj, 'page_title': str(obj),
    })


@login_required
def approvalrule_create(request):
    form = ApprovalRuleForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ApprovalRule', str(obj))
        messages.success(request, f'Approval rule "{obj.name}" created.')
        return redirect('automation:approvalrule_detail', pk=obj.pk)
    return render(request, 'automation/approvalrule_form.html', {
        'form': form, 'page_title': 'Create Approval Rule',
    })


@login_required
def approvalrule_edit(request, pk):
    obj = get_object_or_404(ApprovalRule, pk=pk, tenant=request.tenant)
    form = ApprovalRuleForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ApprovalRule', str(obj))
        messages.success(request, f'Approval rule "{obj.name}" updated.')
        return redirect('automation:approvalrule_detail', pk=obj.pk)
    return render(request, 'automation/approvalrule_form.html', {
        'form': form, 'approvalrule': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def approvalrule_delete(request, pk):
    obj = get_object_or_404(ApprovalRule, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ApprovalRule', label)
        messages.success(request, 'Approval rule deleted.')
        return redirect('automation:approvalrule_list')
    return redirect('automation:approvalrule_list')


# ---------------------------------------------------------------------------
# Notification rules
# ---------------------------------------------------------------------------
@login_required
def notificationrule_list(request):
    qs = NotificationRule.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(recipient_role__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    channel = request.GET.get('channel', '').strip()
    if channel:
        qs = qs.filter(channel=channel)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'automation/notificationrule_list.html', {
        'page_title': 'Notification Rules',
        'page_obj': page_obj,
        'notification_rules': page_obj.object_list,
        'status_choices': NotificationRule.STATUS_CHOICES,
        'channel_choices': NotificationRule.CHANNEL_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def notificationrule_detail(request, pk):
    obj = get_object_or_404(NotificationRule, pk=pk, tenant=request.tenant)
    return render(request, 'automation/notificationrule_detail.html', {
        'notificationrule': obj, 'page_title': str(obj),
    })


@login_required
def notificationrule_create(request):
    form = NotificationRuleForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'NotificationRule', str(obj))
        messages.success(request, f'Notification rule "{obj.name}" created.')
        return redirect('automation:notificationrule_detail', pk=obj.pk)
    return render(request, 'automation/notificationrule_form.html', {
        'form': form, 'page_title': 'Create Notification Rule',
    })


@login_required
def notificationrule_edit(request, pk):
    obj = get_object_or_404(NotificationRule, pk=pk, tenant=request.tenant)
    form = NotificationRuleForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'NotificationRule', str(obj))
        messages.success(request, f'Notification rule "{obj.name}" updated.')
        return redirect('automation:notificationrule_detail', pk=obj.pk)
    return render(request, 'automation/notificationrule_form.html', {
        'form': form, 'notificationrule': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def notificationrule_delete(request, pk):
    obj = get_object_or_404(NotificationRule, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'NotificationRule', label)
        messages.success(request, 'Notification rule deleted.')
        return redirect('automation:notificationrule_list')
    return redirect('automation:notificationrule_list')


# ---------------------------------------------------------------------------
# Recurring rules
# ---------------------------------------------------------------------------
@login_required
def recurringrule_list(request):
    qs = RecurringRule.objects.filter(tenant=request.tenant).select_related(
        'project', 'assignee',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(task_template__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    frequency = request.GET.get('frequency', '').strip()
    if frequency:
        qs = qs.filter(frequency=frequency)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'automation/recurringrule_list.html', {
        'page_title': 'Recurring Rules',
        'page_obj': page_obj,
        'recurring_rules': page_obj.object_list,
        'status_choices': RecurringRule.STATUS_CHOICES,
        'frequency_choices': RecurringRule.FREQUENCY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def recurringrule_detail(request, pk):
    obj = get_object_or_404(RecurringRule, pk=pk, tenant=request.tenant)
    return render(request, 'automation/recurringrule_detail.html', {
        'recurringrule': obj, 'page_title': str(obj),
    })


@login_required
def recurringrule_create(request):
    form = RecurringRuleForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'RecurringRule', str(obj))
        messages.success(request, f'Recurring rule "{obj.name}" created.')
        return redirect('automation:recurringrule_detail', pk=obj.pk)
    return render(request, 'automation/recurringrule_form.html', {
        'form': form, 'page_title': 'Create Recurring Rule',
    })


@login_required
def recurringrule_edit(request, pk):
    obj = get_object_or_404(RecurringRule, pk=pk, tenant=request.tenant)
    form = RecurringRuleForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'RecurringRule', str(obj))
        messages.success(request, f'Recurring rule "{obj.name}" updated.')
        return redirect('automation:recurringrule_detail', pk=obj.pk)
    return render(request, 'automation/recurringrule_form.html', {
        'form': form, 'recurringrule': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def recurringrule_delete(request, pk):
    obj = get_object_or_404(RecurringRule, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'RecurringRule', label)
        messages.success(request, 'Recurring rule deleted.')
        return redirect('automation:recurringrule_list')
    return redirect('automation:recurringrule_list')


# ---------------------------------------------------------------------------
# Automation hooks
# ---------------------------------------------------------------------------
@login_required
def automationhook_list(request):
    qs = AutomationHook.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(event__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    hook_type = request.GET.get('hook_type', '').strip()
    if hook_type:
        qs = qs.filter(hook_type=hook_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'automation/automationhook_list.html', {
        'page_title': 'Automation Hooks',
        'page_obj': page_obj,
        'automation_hooks': page_obj.object_list,
        'status_choices': AutomationHook.STATUS_CHOICES,
        'hook_type_choices': AutomationHook.HOOK_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def automationhook_detail(request, pk):
    obj = get_object_or_404(AutomationHook, pk=pk, tenant=request.tenant)
    return render(request, 'automation/automationhook_detail.html', {
        'automationhook': obj, 'page_title': str(obj),
    })


@login_required
def automationhook_create(request):
    form = AutomationHookForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'AutomationHook', str(obj))
        messages.success(request, f'Automation hook "{obj.name}" created.')
        return redirect('automation:automationhook_detail', pk=obj.pk)
    return render(request, 'automation/automationhook_form.html', {
        'form': form, 'page_title': 'Create Automation Hook',
    })


@login_required
def automationhook_edit(request, pk):
    obj = get_object_or_404(AutomationHook, pk=pk, tenant=request.tenant)
    form = AutomationHookForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'AutomationHook', str(obj))
        messages.success(request, f'Automation hook "{obj.name}" updated.')
        return redirect('automation:automationhook_detail', pk=obj.pk)
    return render(request, 'automation/automationhook_form.html', {
        'form': form, 'automationhook': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def automationhook_delete(request, pk):
    obj = get_object_or_404(AutomationHook, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'AutomationHook', label)
        messages.success(request, 'Automation hook deleted.')
        return redirect('automation:automationhook_list')
    return redirect('automation:automationhook_list')
