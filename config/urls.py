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
    # Module 4 - Cost & Budget Management.
    path('budgeting/', include('apps.budgeting.urls')),
    # Module 5 - Risk & Issue Management.
    path('risks/', include('apps.risks.urls')),
    # Module 6 - Quality Management.
    path('quality/', include('apps.quality.urls')),
    # Module 7 - Scope & Requirements Management.
    path('scope/', include('apps.scope.urls')),
    # Module 8 - Task & Work Management.
    path('work/', include('apps.work.urls')),
    # Module 9 - Collaboration & Communication.
    path('collaboration/', include('apps.collaboration.urls')),
    # Module 10 - Document & Knowledge Management.
    path('documents/', include('apps.documents.urls')),
    # Module 11 - Time & Attendance Tracking.
    path('timesheets/', include('apps.timesheets.urls')),
    # Module 12 - Portfolio & Program Management.
    path('portfolio/', include('apps.portfolio.urls')),
    # Module 13 - Agile & Scrum Management.
    path('agile/', include('apps.agile.urls')),
    # Module 14 - Client & External Collaboration.
    path('clients/', include('apps.clients.urls')),
    # Module 15 - Financial & Billing Management.
    path('finance/', include('apps.finance.urls')),
    # Core: module placeholders + audit log.
    path('', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
