from django.contrib import admin
from .models import MaintenanceRequest

@admin.register(MaintenanceRequest)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['device', 'priority', 'status', 'reported_by', 'reported_on']
    list_filter = ['status', 'priority']