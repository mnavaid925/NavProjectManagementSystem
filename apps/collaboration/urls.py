from django.urls import path

from . import views

app_name = 'collaboration'

urlpatterns = [
    # Channels
    path('channels/', views.channel_list, name='channel_list'),
    path('channels/create/', views.channel_create, name='channel_create'),
    path('channels/<int:pk>/', views.channel_detail, name='channel_detail'),
    path('channels/<int:pk>/edit/', views.channel_edit, name='channel_edit'),
    path('channels/<int:pk>/delete/', views.channel_delete, name='channel_delete'),
    # Shared documents
    path('shared-documents/', views.shareddocument_list, name='shareddocument_list'),
    path('shared-documents/create/', views.shareddocument_create, name='shareddocument_create'),
    path('shared-documents/<int:pk>/', views.shareddocument_detail, name='shareddocument_detail'),
    path('shared-documents/<int:pk>/edit/', views.shareddocument_edit, name='shareddocument_edit'),
    path('shared-documents/<int:pk>/delete/', views.shareddocument_delete, name='shareddocument_delete'),
    # Meetings
    path('meetings/', views.meeting_list, name='meeting_list'),
    path('meetings/create/', views.meeting_create, name='meeting_create'),
    path('meetings/<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('meetings/<int:pk>/edit/', views.meeting_edit, name='meeting_edit'),
    path('meetings/<int:pk>/delete/', views.meeting_delete, name='meeting_delete'),
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    path('notifications/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:pk>/edit/', views.notification_edit, name='notification_edit'),
    path('notifications/<int:pk>/delete/', views.notification_delete, name='notification_delete'),
    # Activity entries
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/create/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activities/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),
]
