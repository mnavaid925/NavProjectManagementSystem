"""Shared helpers: client IP extraction and audit logging."""
from .models import AuditLog


def get_client_ip(request):
    """Best-effort extraction of the client IP address from the request."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, entity, object_repr='', changes=''):
    """Write a tenant-scoped AuditLog row for a meaningful user action."""
    user = getattr(request, 'user', None)
    return AuditLog.objects.create(
        tenant=getattr(request, 'tenant', None),
        user=user if (user is not None and user.is_authenticated) else None,
        action=action,
        entity=entity,
        object_repr=str(object_repr)[:255],
        changes=changes,
        ip_address=get_client_ip(request),
    )
