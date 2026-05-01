from .models import Alert
from maintenance.models import MaintenanceRequest

def alerts_processor(request):
    if request.user.is_authenticated:
        # Count general alerts
        unread_alerts = Alert.objects.filter(is_dismissed=False).count()
        recent_alerts = Alert.objects.filter(is_dismissed=False)[:5]
        
        # Count pending maintenance requests
        pending_maintenance = MaintenanceRequest.objects.filter(status='pending').count()
    else:
        unread_alerts = 0
        recent_alerts = []
        pending_maintenance = 0

    return {
        'unread_alerts_count': unread_alerts,
        'recent_alerts': recent_alerts,
        'pending_maintenance_count': pending_maintenance,
    }