from django.urls import path

from . import views

app_name = 'work'

urlpatterns = [
    # Work items
    path('items/', views.workitem_list, name='workitem_list'),
    path('items/create/', views.workitem_create, name='workitem_create'),
    path('items/<int:pk>/', views.workitem_detail, name='workitem_detail'),
    path('items/<int:pk>/edit/', views.workitem_edit, name='workitem_edit'),
    path('items/<int:pk>/delete/', views.workitem_delete, name='workitem_delete'),
    # Priority scores
    path('priority-scores/', views.priorityscore_list, name='priorityscore_list'),
    path('priority-scores/create/', views.priorityscore_create, name='priorityscore_create'),
    path('priority-scores/<int:pk>/', views.priorityscore_detail, name='priorityscore_detail'),
    path('priority-scores/<int:pk>/edit/', views.priorityscore_edit, name='priorityscore_edit'),
    path('priority-scores/<int:pk>/delete/', views.priorityscore_delete, name='priorityscore_delete'),
    # Board columns
    path('board-columns/', views.boardcolumn_list, name='boardcolumn_list'),
    path('board-columns/create/', views.boardcolumn_create, name='boardcolumn_create'),
    path('board-columns/<int:pk>/', views.boardcolumn_detail, name='boardcolumn_detail'),
    path('board-columns/<int:pk>/edit/', views.boardcolumn_edit, name='boardcolumn_edit'),
    path('board-columns/<int:pk>/delete/', views.boardcolumn_delete, name='boardcolumn_delete'),
    # Board cards
    path('board-cards/', views.boardcard_list, name='boardcard_list'),
    path('board-cards/create/', views.boardcard_create, name='boardcard_create'),
    path('board-cards/<int:pk>/', views.boardcard_detail, name='boardcard_detail'),
    path('board-cards/<int:pk>/edit/', views.boardcard_edit, name='boardcard_edit'),
    path('board-cards/<int:pk>/delete/', views.boardcard_delete, name='boardcard_delete'),
    # Work dependencies
    path('dependencies/', views.workdependency_list, name='workdependency_list'),
    path('dependencies/create/', views.workdependency_create, name='workdependency_create'),
    path('dependencies/<int:pk>/', views.workdependency_detail, name='workdependency_detail'),
    path('dependencies/<int:pk>/edit/', views.workdependency_edit, name='workdependency_edit'),
    path('dependencies/<int:pk>/delete/', views.workdependency_delete, name='workdependency_delete'),
]
