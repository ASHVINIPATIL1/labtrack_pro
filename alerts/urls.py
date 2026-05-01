from django.urls import path
from . import views

urlpatterns = [
    path('dismiss/<int:pk>/', views.dismiss_alert, name='dismiss_alert'),
]