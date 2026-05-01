from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class Department(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name

    def lab_count(self):
        return self.labs.count()


class Lab(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='labs'
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}{' — ' + self.department.name if self.department else ''}"

    def total_purchase_cost(self):
        return sum(
            d.purchase_cost * d.quantity
            for d in self.devices.filter(status='working')
        )

    def total_current_value(self):
        return sum(d.current_value() for d in self.devices.filter(status='working'))

    def working_device_count(self):
        return self.devices.filter(status='working').count()

    def maintenance_count(self):
        return self.devices.filter(status='maintenance').count()

    def trash_count(self):
        return self.devices.filter(status='trash').count()


class DeviceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Device Categories"

    def __str__(self):
        return self.name


class Device(models.Model):
    STATUS_CHOICES = [
        ('working', 'Working'),
        ('maintenance', 'Maintenance'),
        ('trash', 'Trash'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='devices')
    category = models.ForeignKey(DeviceCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    serial_id = models.CharField(max_length=100, unique=True, blank=True)
    os_name = models.TextField(blank=True, default='')
    software_details = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_configuration = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    useful_life_years = models.PositiveIntegerField(default=5)
    salvage_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_threshold = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.lab.name})"

    def annual_depreciation(self):
        return (float(self.purchase_cost) - float(self.salvage_value)) / self.useful_life_years

    def age_years(self):
        delta = timezone.now().date() - self.purchase_date
        return delta.days / 365.25

    def accumulated_depreciation(self):
        dep = self.annual_depreciation() * self.age_years()
        max_dep = float(self.purchase_cost) - float(self.salvage_value)
        return min(dep, max_dep)

    def current_value(self):
        val = float(self.purchase_cost) - self.accumulated_depreciation()
        return max(val, float(self.salvage_value)) * self.quantity

    def depreciation_percent(self):
        if float(self.purchase_cost) == 0:
            return 0
        return min(int((self.accumulated_depreciation() / float(self.purchase_cost)) * 100), 100)

    def is_below_threshold(self):
        return self.quantity < self.min_threshold and self.status == 'working'

    def save(self, *args, **kwargs):
        if not self.serial_id:
            prefix = f"LAB{self.lab_id}-"
            last = Device.objects.filter(serial_id__startswith=prefix).count()
            self.serial_id = f"{prefix}{str(last + 1).zfill(4)}"
        super().save(*args, **kwargs)


class DeviceHistory(models.Model):
    ACTION_CHOICES = [
        ('added', 'Device Added'),
        ('updated', 'Details Updated'),
        ('status_changed', 'Status Changed'),
        ('quantity_changed', 'Quantity Changed'),
        ('moved_maintenance', 'Moved to Maintenance'),
        ('returned_active', 'Returned to Active'),
        ('moved_trash', 'Moved to Trash'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    old_value = models.CharField(max_length=200, blank=True)
    new_value = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.name} - {self.action} at {self.timestamp}"