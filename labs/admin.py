from django.contrib import admin
from .models import Lab, Device, DeviceCategory, DeviceHistory

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at']

@admin.register(DeviceCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'lab', 'status', 'purchase_cost']
    list_filter = ['lab', 'status']
    search_fields = ['name', 'serial_id']

@admin.register(DeviceHistory)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['device', 'action', 'performed_by', 'timestamp']
    list_filter = ['action']