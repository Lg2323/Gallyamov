from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/dashboard/', views.dashboard, name='dashboard'),
    path('requests/create/', views.create_request, name='create_request'),
    path('requests/<int:pk>/review/', views.review_create, name='review_create'),
    path('control/requests/', views.admin_requests, name='admin_requests'),
    path('control/requests/<int:pk>/', views.admin_request_detail, name='admin_request_detail'),
]
