from django.urls import path

from . import views

app_name = 'automation'

urlpatterns = [
    # Workflows
    path('workflows/', views.workflowdefinition_list, name='workflowdefinition_list'),
    path('workflows/create/', views.workflowdefinition_create, name='workflowdefinition_create'),
    path('workflows/<int:pk>/', views.workflowdefinition_detail, name='workflowdefinition_detail'),
    path('workflows/<int:pk>/edit/', views.workflowdefinition_edit, name='workflowdefinition_edit'),
    path('workflows/<int:pk>/delete/', views.workflowdefinition_delete, name='workflowdefinition_delete'),
    # Approval rules
    path('approval-rules/', views.approvalrule_list, name='approvalrule_list'),
    path('approval-rules/create/', views.approvalrule_create, name='approvalrule_create'),
    path('approval-rules/<int:pk>/', views.approvalrule_detail, name='approvalrule_detail'),
    path('approval-rules/<int:pk>/edit/', views.approvalrule_edit, name='approvalrule_edit'),
    path('approval-rules/<int:pk>/delete/', views.approvalrule_delete, name='approvalrule_delete'),
    # Notification rules
    path('notification-rules/', views.notificationrule_list, name='notificationrule_list'),
    path('notification-rules/create/', views.notificationrule_create, name='notificationrule_create'),
    path('notification-rules/<int:pk>/', views.notificationrule_detail, name='notificationrule_detail'),
    path('notification-rules/<int:pk>/edit/', views.notificationrule_edit, name='notificationrule_edit'),
    path('notification-rules/<int:pk>/delete/', views.notificationrule_delete, name='notificationrule_delete'),
    # Recurring rules
    path('recurring-rules/', views.recurringrule_list, name='recurringrule_list'),
    path('recurring-rules/create/', views.recurringrule_create, name='recurringrule_create'),
    path('recurring-rules/<int:pk>/', views.recurringrule_detail, name='recurringrule_detail'),
    path('recurring-rules/<int:pk>/edit/', views.recurringrule_edit, name='recurringrule_edit'),
    path('recurring-rules/<int:pk>/delete/', views.recurringrule_delete, name='recurringrule_delete'),
    # Automation hooks
    path('hooks/', views.automationhook_list, name='automationhook_list'),
    path('hooks/create/', views.automationhook_create, name='automationhook_create'),
    path('hooks/<int:pk>/', views.automationhook_detail, name='automationhook_detail'),
    path('hooks/<int:pk>/edit/', views.automationhook_edit, name='automationhook_edit'),
    path('hooks/<int:pk>/delete/', views.automationhook_delete, name='automationhook_delete'),
]
