from django.urls import path

from . import views

app_name = 'reporting'

urlpatterns = [
    # Report definitions
    path('report-definitions/', views.reportdefinition_list, name='reportdefinition_list'),
    path('report-definitions/create/', views.reportdefinition_create, name='reportdefinition_create'),
    path('report-definitions/<int:pk>/', views.reportdefinition_detail, name='reportdefinition_detail'),
    path('report-definitions/<int:pk>/edit/', views.reportdefinition_edit, name='reportdefinition_edit'),
    path('report-definitions/<int:pk>/delete/', views.reportdefinition_delete, name='reportdefinition_delete'),
    # Report runs
    path('report-runs/', views.reportrun_list, name='reportrun_list'),
    path('report-runs/create/', views.reportrun_create, name='reportrun_create'),
    path('report-runs/<int:pk>/', views.reportrun_detail, name='reportrun_detail'),
    path('report-runs/<int:pk>/edit/', views.reportrun_edit, name='reportrun_edit'),
    path('report-runs/<int:pk>/delete/', views.reportrun_delete, name='reportrun_delete'),
    # Dashboard widgets
    path('widgets/', views.dashboardwidget_list, name='dashboardwidget_list'),
    path('widgets/create/', views.dashboardwidget_create, name='dashboardwidget_create'),
    path('widgets/<int:pk>/', views.dashboardwidget_detail, name='dashboardwidget_detail'),
    path('widgets/<int:pk>/edit/', views.dashboardwidget_edit, name='dashboardwidget_edit'),
    path('widgets/<int:pk>/delete/', views.dashboardwidget_delete, name='dashboardwidget_delete'),
    # Executive packs
    path('executive-packs/', views.executivepack_list, name='executivepack_list'),
    path('executive-packs/create/', views.executivepack_create, name='executivepack_create'),
    path('executive-packs/<int:pk>/', views.executivepack_detail, name='executivepack_detail'),
    path('executive-packs/<int:pk>/edit/', views.executivepack_edit, name='executivepack_edit'),
    path('executive-packs/<int:pk>/delete/', views.executivepack_delete, name='executivepack_delete'),
    # Data exports
    path('data-exports/', views.dataexport_list, name='dataexport_list'),
    path('data-exports/create/', views.dataexport_create, name='dataexport_create'),
    path('data-exports/<int:pk>/', views.dataexport_detail, name='dataexport_detail'),
    path('data-exports/<int:pk>/edit/', views.dataexport_edit, name='dataexport_edit'),
    path('data-exports/<int:pk>/delete/', views.dataexport_delete, name='dataexport_delete'),
]
