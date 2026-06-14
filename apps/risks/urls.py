from django.urls import path

from . import views

app_name = 'risks'

urlpatterns = [
    # Risks (Risk Register)
    path('register/', views.risk_list, name='risk_list'),
    path('register/create/', views.risk_create, name='risk_create'),
    path('register/<int:pk>/', views.risk_detail, name='risk_detail'),
    path('register/<int:pk>/edit/', views.risk_edit, name='risk_edit'),
    path('register/<int:pk>/delete/', views.risk_delete, name='risk_delete'),
    # Risk analyses
    path('analysis/', views.analysis_list, name='analysis_list'),
    path('analysis/create/', views.analysis_create, name='analysis_create'),
    path('analysis/<int:pk>/', views.analysis_detail, name='analysis_detail'),
    path('analysis/<int:pk>/edit/', views.analysis_edit, name='analysis_edit'),
    path('analysis/<int:pk>/delete/', views.analysis_delete, name='analysis_delete'),
    # Risk responses
    path('responses/', views.response_list, name='response_list'),
    path('responses/create/', views.response_create, name='response_create'),
    path('responses/<int:pk>/', views.response_detail, name='response_detail'),
    path('responses/<int:pk>/edit/', views.response_edit, name='response_edit'),
    path('responses/<int:pk>/delete/', views.response_delete, name='response_delete'),
    # Issues (Issue Log)
    path('issues/', views.issue_list, name='issue_list'),
    path('issues/create/', views.issue_create, name='issue_create'),
    path('issues/<int:pk>/', views.issue_detail, name='issue_detail'),
    path('issues/<int:pk>/edit/', views.issue_edit, name='issue_edit'),
    path('issues/<int:pk>/delete/', views.issue_delete, name='issue_delete'),
    # Risk reviews
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/create/', views.review_create, name='review_create'),
    path('reviews/<int:pk>/', views.review_detail, name='review_detail'),
    path('reviews/<int:pk>/edit/', views.review_edit, name='review_edit'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
]
