"""Core views: generic module placeholder + audit log list."""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from .models import AuditLog
from .navigation import find_submodule


@login_required
def module_placeholder(request, module_slug, sub_slug):
    """Render a 'coming soon' page for any not-yet-built sub-module."""
    module, submodule = find_submodule(module_slug, sub_slug)
    if module is None or submodule is None:
        raise Http404('Unknown module or sub-module.')
    context = {
        'module': module,
        'submodule': submodule,
        'page_title': submodule['name'],
        'module_number': module['number'],
    }
    return render(request, 'core/module_placeholder.html', context)


@login_required
def audit_log_view(request):
    """List AuditLog entries for the current tenant with search + pagination."""
    qs = AuditLog.objects.filter(tenant=request.tenant).select_related('user')

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(action__icontains=q)
            | Q(entity__icontains=q)
            | Q(object_repr__icontains=q)
            | Q(user__username__icontains=q)
        )

    action = request.GET.get('action', '').strip()
    if action:
        qs = qs.filter(action=action)

    actions = (
        AuditLog.objects.filter(tenant=request.tenant)
        .values_list('action', flat=True)
        .distinct()
        .order_by('action')
    )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_title': 'Audit Trail & Logging',
        'page_obj': page_obj,
        'logs': page_obj.object_list,
        'actions': actions,
        'total_count': paginator.count,
    }
    return render(request, 'core/audit_log.html', context)
