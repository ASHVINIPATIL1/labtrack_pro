from django.db import models
from django.contrib.auth.models import User
from labs.models import Lab, Device


class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('low_stock', 'Low Stock'),
        ('maintenance', 'Device in Maintenance'),
        ('trash', 'Device Moved to Trash'),
        ('fully_depreciated', 'Fully Depreciated'),
    ]

    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='alerts')
    message = models.TextField()
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    dismissed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.alert_type} - {self.device.name}"