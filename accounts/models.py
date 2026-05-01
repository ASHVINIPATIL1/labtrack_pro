from django.db import models
from django.contrib.auth.models import User
from labs.models import Lab


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Lab Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    assigned_lab = models.ForeignKey(
        Lab, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="For staff: which lab they manage"
    )
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'