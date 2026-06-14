"""URL configuration for the NavPMS project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication, user & role management, profile, preferences.
    path('', include('apps.accounts.urls')),
    # Dashboard at the site root.
    path('', include('apps.dashboard.urls')),
    # Module 0 - Tenant & Subscription Management.
    path('tenants/', include('apps.tenants.urls')),
    # Workspace demo (projects, tasks, meetings, tickets, invoices).
    path('projects/', include('apps.projects.urls')),
    # Module 1 - Project Initiation & Charter.
    path('initiation/', include('apps.initiation.urls')),
    # Module 2 - Project Planning & Scheduling.
    path('planning/', include('apps.planning.urls')),
    # Module 3 - Resource Management.
    path('resources/', include('apps.resources.urls')),
    # Core: module placeholders + audit log.
    path('', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
