from django.urls import path

from . import views

app_name = 'administration'

urlpatterns = [
    # Security policies
    path('security-policies/', views.securitypolicy_list, name='securitypolicy_list'),
    path('security-policies/create/', views.securitypolicy_create, name='securitypolicy_create'),
    path('security-policies/<int:pk>/', views.securitypolicy_detail, name='securitypolicy_detail'),
    path('security-policies/<int:pk>/edit/', views.securitypolicy_edit, name='securitypolicy_edit'),
    path('security-policies/<int:pk>/delete/', views.securitypolicy_delete, name='securitypolicy_delete'),
    # Compliance items
    path('compliance/', views.complianceitem_list, name='complianceitem_list'),
    path('compliance/create/', views.complianceitem_create, name='complianceitem_create'),
    path('compliance/<int:pk>/', views.complianceitem_detail, name='complianceitem_detail'),
    path('compliance/<int:pk>/edit/', views.complianceitem_edit, name='complianceitem_edit'),
    path('compliance/<int:pk>/delete/', views.complianceitem_delete, name='complianceitem_delete'),
    # Backup jobs
    path('backup-jobs/', views.backupjob_list, name='backupjob_list'),
    path('backup-jobs/create/', views.backupjob_create, name='backupjob_create'),
    path('backup-jobs/<int:pk>/', views.backupjob_detail, name='backupjob_detail'),
    path('backup-jobs/<int:pk>/edit/', views.backupjob_edit, name='backupjob_edit'),
    path('backup-jobs/<int:pk>/delete/', views.backupjob_delete, name='backupjob_delete'),
    # System health metrics
    path('health-metrics/', views.systemhealthmetric_list, name='systemhealthmetric_list'),
    path('health-metrics/create/', views.systemhealthmetric_create, name='systemhealthmetric_create'),
    path('health-metrics/<int:pk>/', views.systemhealthmetric_detail, name='systemhealthmetric_detail'),
    path('health-metrics/<int:pk>/edit/', views.systemhealthmetric_edit, name='systemhealthmetric_edit'),
    path('health-metrics/<int:pk>/delete/', views.systemhealthmetric_delete, name='systemhealthmetric_delete'),
    # Access reviews
    path('access-reviews/', views.accessreview_list, name='accessreview_list'),
    path('access-reviews/create/', views.accessreview_create, name='accessreview_create'),
    path('access-reviews/<int:pk>/', views.accessreview_detail, name='accessreview_detail'),
    path('access-reviews/<int:pk>/edit/', views.accessreview_edit, name='accessreview_edit'),
    path('access-reviews/<int:pk>/delete/', views.accessreview_delete, name='accessreview_delete'),
]
