"""Tenant resolution middleware."""


class TenantMiddleware:
    """
    Attaches request.tenant from the authenticated user's tenant.

    For anonymous users (and the superuser, which has tenant=None) request.tenant
    is None, which by design causes tenant-scoped queries to return empty results.
    Must be placed AFTER AuthenticationMiddleware so request.user is available.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            request.tenant = getattr(user, 'tenant', None)
        else:
            request.tenant = None
        return self.get_response(request)
