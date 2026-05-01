from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/<int:pk>/edit/', views.edit_department, name='edit_department'),
    path('departments/<int:pk>/delete/', views.delete_department, name='delete_department'),
    path('labs/', views.lab_list, name='lab_list'),
    path('labs/add/', views.add_lab, name='add_lab'),
    path('labs/add/<int:dept_pk>/', views.add_lab, name='add_lab_in_department'),
    path('labs/<int:pk>/', views.lab_detail, name='lab_detail'),
    path('labs/<int:pk>/edit/', views.edit_lab, name='edit_lab'),
    path('labs/<int:pk>/delete/', views.delete_lab, name='delete_lab'),
    path('devices/add/<int:lab_pk>/', views.add_device, name='add_device'),
    path('devices/<int:pk>/', views.device_detail, name='device_detail'),
    path('devices/<int:pk>/edit/', views.edit_device, name='edit_device'),
    path('devices/<int:pk>/status/', views.change_device_status, name='change_device_status'),
    path('devices/<int:pk>/delete/', views.delete_device, name='delete_device'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
]