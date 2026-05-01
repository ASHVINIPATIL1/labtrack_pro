import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from accounts.models import UserProfile
from labs.models import Lab


def _get_user_labs(user):
    try:
        profile = user.profile
        if profile.role == 'admin':
            return Lab.objects.all()
        if profile.assigned_lab:
            return Lab.objects.filter(pk=profile.assigned_lab.pk)
    except UserProfile.DoesNotExist:
        pass
    return Lab.objects.none()


@login_required
def reports_home(request):
    labs = _get_user_labs(request.user)
    
    # Calculate lab statistics
    lab_stats = []
    working_count = 0
    maintenance_count = 0
    trash_count = 0
    issues_count = 0
    
    for lab in labs:
        working = lab.devices.filter(status='working').count()
        maintenance = lab.devices.filter(status='maintenance').count()
        trash = lab.devices.filter(status='trash').count()
        issues = lab.devices.aggregate(
            total=Count('maintenance_requests', filter=Q(maintenance_requests__status='pending'))
        )['total'] or 0
        
        lab_stats.append({
            'lab': lab,
            'working': working,
            'maintenance': maintenance,
            'trash': trash,
            'issues': issues,
        })
        
        working_count += working
        maintenance_count += maintenance
        trash_count += trash
        issues_count += issues
    
    context = {
        'labs': labs,
        'lab_stats': lab_stats,
        'working_count': working_count,
        'maintenance_count': maintenance_count,
        'trash_count': trash_count,
        'issues_count': issues_count,
    }
    return render(request, 'reports/reports_home.html', context)


@login_required
def export_report_csv(request):
    labs = _get_user_labs(request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="labtrack_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Lab', 'Department', 'Working Devices', 'Maintenance Devices', 'Trash Devices', 'Issues'])

    for lab in labs:
        working = lab.devices.filter(status='working').count()
        maintenance = lab.devices.filter(status='maintenance').count()
        trash = lab.devices.filter(status='trash').count()
        issues = lab.devices.aggregate(
            total=Count('maintenance_requests', filter=Q(maintenance_requests__status='pending'))
        )['total'] or 0
        writer.writerow([lab.name, lab.department.name if lab.department else 'Unassigned', working, maintenance, trash, issues])

    return response