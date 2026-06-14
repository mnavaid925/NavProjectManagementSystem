from django.urls import path

from . import views

app_name = 'timesheets'

urlpatterns = [
    # Timesheets
    path('timesheets/', views.timesheet_list, name='timesheet_list'),
    path('timesheets/create/', views.timesheet_create, name='timesheet_create'),
    path('timesheets/<int:pk>/', views.timesheet_detail, name='timesheet_detail'),
    path('timesheets/<int:pk>/edit/', views.timesheet_edit, name='timesheet_edit'),
    path('timesheets/<int:pk>/delete/', views.timesheet_delete, name='timesheet_delete'),
    # Timesheet lines
    path('timesheet-lines/', views.timesheetline_list, name='timesheetline_list'),
    path('timesheet-lines/create/', views.timesheetline_create, name='timesheetline_create'),
    path('timesheet-lines/<int:pk>/', views.timesheetline_detail, name='timesheetline_detail'),
    path('timesheet-lines/<int:pk>/edit/', views.timesheetline_edit, name='timesheetline_edit'),
    path('timesheet-lines/<int:pk>/delete/', views.timesheetline_delete, name='timesheetline_delete'),
    # Timesheet approvals
    path('approvals/', views.timesheetapproval_list, name='timesheetapproval_list'),
    path('approvals/create/', views.timesheetapproval_create, name='timesheetapproval_create'),
    path('approvals/<int:pk>/', views.timesheetapproval_detail, name='timesheetapproval_detail'),
    path('approvals/<int:pk>/edit/', views.timesheetapproval_edit, name='timesheetapproval_edit'),
    path('approvals/<int:pk>/delete/', views.timesheetapproval_delete, name='timesheetapproval_delete'),
    # Leave records
    path('leave/', views.leaverecord_list, name='leaverecord_list'),
    path('leave/create/', views.leaverecord_create, name='leaverecord_create'),
    path('leave/<int:pk>/', views.leaverecord_detail, name='leaverecord_detail'),
    path('leave/<int:pk>/edit/', views.leaverecord_edit, name='leaverecord_edit'),
    path('leave/<int:pk>/delete/', views.leaverecord_delete, name='leaverecord_delete'),
    # Utilization snapshots
    path('utilization/', views.utilizationsnapshot_list, name='utilizationsnapshot_list'),
    path('utilization/create/', views.utilizationsnapshot_create, name='utilizationsnapshot_create'),
    path('utilization/<int:pk>/', views.utilizationsnapshot_detail, name='utilizationsnapshot_detail'),
    path('utilization/<int:pk>/edit/', views.utilizationsnapshot_edit, name='utilizationsnapshot_edit'),
    path('utilization/<int:pk>/delete/', views.utilizationsnapshot_delete, name='utilizationsnapshot_delete'),
]
