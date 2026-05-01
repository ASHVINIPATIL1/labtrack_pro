from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('export/', views.export_report_csv, name='export_report_csv'),
]