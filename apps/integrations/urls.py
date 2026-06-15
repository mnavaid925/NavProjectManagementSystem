from django.urls import path

from . import views

app_name = 'integrations'

urlpatterns = [
    # Connectors
    path('connectors/', views.connector_list, name='connector_list'),
    path('connectors/create/', views.connector_create, name='connector_create'),
    path('connectors/<int:pk>/', views.connector_detail, name='connector_detail'),
    path('connectors/<int:pk>/edit/', views.connector_edit, name='connector_edit'),
    path('connectors/<int:pk>/delete/', views.connector_delete, name='connector_delete'),
    # Sync jobs
    path('sync-jobs/', views.syncjob_list, name='syncjob_list'),
    path('sync-jobs/create/', views.syncjob_create, name='syncjob_create'),
    path('sync-jobs/<int:pk>/', views.syncjob_detail, name='syncjob_detail'),
    path('sync-jobs/<int:pk>/edit/', views.syncjob_edit, name='syncjob_edit'),
    path('sync-jobs/<int:pk>/delete/', views.syncjob_delete, name='syncjob_delete'),
    # Sync logs
    path('sync-logs/', views.synclog_list, name='synclog_list'),
    path('sync-logs/create/', views.synclog_create, name='synclog_create'),
    path('sync-logs/<int:pk>/', views.synclog_detail, name='synclog_detail'),
    path('sync-logs/<int:pk>/edit/', views.synclog_edit, name='synclog_edit'),
    path('sync-logs/<int:pk>/delete/', views.synclog_delete, name='synclog_delete'),
    # Webhooks
    path('webhooks/', views.webhook_list, name='webhook_list'),
    path('webhooks/create/', views.webhook_create, name='webhook_create'),
    path('webhooks/<int:pk>/', views.webhook_detail, name='webhook_detail'),
    path('webhooks/<int:pk>/edit/', views.webhook_edit, name='webhook_edit'),
    path('webhooks/<int:pk>/delete/', views.webhook_delete, name='webhook_delete'),
    # API keys
    path('api-keys/', views.apikey_list, name='apikey_list'),
    path('api-keys/create/', views.apikey_create, name='apikey_create'),
    path('api-keys/<int:pk>/', views.apikey_detail, name='apikey_detail'),
    path('api-keys/<int:pk>/edit/', views.apikey_edit, name='apikey_edit'),
    path('api-keys/<int:pk>/delete/', views.apikey_delete, name='apikey_delete'),
]
