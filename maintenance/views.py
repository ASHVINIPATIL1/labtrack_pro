from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import MaintenanceRequest
from labs.models import Device, DeviceHistory
from .forms import MaintenanceForm, PublicIssueForm, ResolveForm


def add_issue(request):
    form = PublicIssueForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        device_id = form.cleaned_data['device_id'].strip()
        device = Device.objects.filter(serial_id__iexact=device_id).first()
        if not device:
            messages.error(request, 'Device not found. Please check the Device ID.')
        else:
            req = MaintenanceRequest.objects.create(
                device=device,
                issue_description=form.cleaned_data['issue_description'],
                reported_by=None,
                status='pending'
            )
            messages.success(request, f'Issue registered for {device.name}. Lab staff will review it shortly.')
            return redirect('report_issue')
    return render(request, 'maintenance/public_issue_form.html', {'form': form})


@login_required
def maintenance_list(request):
    requests = MaintenanceRequest.objects.select_related('device', 'device__lab', 'reported_by')
    if hasattr(request.user, 'profile') and request.user.profile.role == 'staff' and request.user.profile.assigned_lab:
        requests = requests.filter(device__lab=request.user.profile.assigned_lab)
    requests = requests.order_by('-reported_on')
    
    pending_requests = requests.filter(status='pending')
    resolved_requests = requests.filter(status='done')
    
    context = {
        'requests': requests,
        'pending_requests': pending_requests,
        'resolved_requests': resolved_requests,
        'pending_count': pending_requests.count(),
        'resolved_count': resolved_requests.count(),
    }
    return render(request, 'maintenance/maintenance_list.html', context)


@login_required
def add_maintenance(request, device_pk):
    device = get_object_or_404(Device, pk=device_pk)
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ['admin', 'staff']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    form = MaintenanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        req = form.save(commit=False)
        req.device = device
        req.reported_by = request.user
        req.status = 'pending'
        req.save()
        DeviceHistory.objects.create(
            device=device,
            action='status_changed',
            performed_by=request.user,
            notes=req.issue_description
        )
        messages.success(request, 'Maintenance request created.')
        return redirect('device_detail', pk=device_pk)
    return render(request, 'maintenance/maintenance_form.html', {'form': form, 'device': device})


@login_required
def resolve_maintenance(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    if request.user.profile.role == 'staff' and request.user.profile.assigned_lab != req.device.lab:
        messages.error(request, 'You can only update issues for your assigned lab.')
        return redirect('maintenance_list')

    form = ResolveForm(request.POST or None, initial={'status': req.status})
    if request.method == 'POST' and form.is_valid():
        req.status = form.cleaned_data['status']
        req.resolution_notes = form.cleaned_data['resolution_notes']
        if req.status == 'done':
            req.resolved_by = request.user
            req.resolved_on = timezone.now()
        else:
            req.resolved_by = None
            req.resolved_on = None
        req.save()
        DeviceHistory.objects.create(
            device=req.device,
            action='status_changed',
            performed_by=request.user,
            notes=f'Issue marked {req.status}. {req.resolution_notes}'
        )
        messages.success(request, 'Issue status updated.')
        return redirect('maintenance_list')
    return render(request, 'maintenance/resolve_form.html', {'form': form, 'req': req})
