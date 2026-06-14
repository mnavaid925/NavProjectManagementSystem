from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('m/<slug:module_slug>/<slug:sub_slug>/', views.module_placeholder, name='module_placeholder'),
    path('audit-log/', views.audit_log_view, name='audit_log'),
]
