from django.urls import path
from . import views

urlpatterns = [
    path('', views.maintenance_list, name='maintenance_list'),
    path('report/', views.add_issue, name='report_issue'),
    path('add/<int:device_pk>/', views.add_maintenance, name='add_maintenance'),
    path('<int:pk>/resolve/', views.resolve_maintenance, name='resolve_maintenance'),
]