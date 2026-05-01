from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from .models import Department, Lab, Device, DeviceCategory, DeviceHistory
from .forms import DepartmentForm, LabForm, DeviceForm, DeviceCategoryForm, DeviceStatusForm
from alerts.models import Alert
from accounts.models import UserProfile


def get_user_labs(user):
    """Return labs accessible to the user based on role."""
    try:
        profile = user.profile
        if profile.role == 'admin':
            return Lab.objects.all()
        elif profile.assigned_lab:
            return Lab.objects.filter(pk=profile.assigned_lab.pk)
    except UserProfile.DoesNotExist:
        pass
    return Lab.objects.all()


@login_required
def dashboard(request):
    labs = get_user_labs(request.user)

    # Ensure profile exists
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={'role': 'admin'}
    )

    total_devices = Device.objects.filter(lab__in=labs, status='working').count()
    total_purchase_cost = sum(
        d.purchase_cost * d.quantity
        for d in Device.objects.filter(lab__in=labs, status='working')
    )
    total_current_value = sum(
        d.current_value()
        for d in Device.objects.filter(lab__in=labs, status='working')
    )
    maintenance_count = Device.objects.filter(lab__in=labs, status='maintenance').count()
    trash_count = Device.objects.filter(lab__in=labs, status='trash').count()
    active_alerts = Alert.objects.filter(lab__in=labs, is_dismissed=False)

    # Category breakdown for chart
    categories = DeviceCategory.objects.all()
    category_data = []
    for cat in categories:
        cost = sum(
            float(d.purchase_cost) * d.quantity
            for d in Device.objects.filter(lab__in=labs, category=cat, status='working')
        )
        if cost > 0:
            category_data.append({'name': cat.name, 'cost': cost})

    # Recent history
    recent_history = DeviceHistory.objects.filter(
        device__lab__in=labs
    ).select_related('device', 'performed_by').order_by('-timestamp')[:8]

    context = {
        'labs': labs,
        'total_devices': total_devices,
        'total_purchase_cost': total_purchase_cost,
        'total_current_value': total_current_value,
        'maintenance_count': maintenance_count,
        'trash_count': trash_count,
        'active_alerts': active_alerts,
        'category_data': category_data,
        'recent_history': recent_history,
        'total_labs': labs.count(),
    }
    return render(request, 'labs/dashboard.html', context)


@login_required
def lab_list(request):
    labs = get_user_labs(request.user)
    return render(request, 'labs/lab_list.html', {'labs': labs})


@login_required
def add_lab(request, dept_pk=None):
    try:
        if request.user.profile.role != 'admin':
            messages.error(request, 'Only admins can add labs.')
            return redirect('lab_list')
    except UserProfile.DoesNotExist:
        pass

    if not Department.objects.exists() and not dept_pk:
        messages.warning(request, 'Please create a department before adding a lab.')
        return redirect('department_list')

    initial = {}
    if dept_pk:
        department = get_object_or_404(Department, pk=dept_pk)
        initial['department'] = department
    else:
        department = None

    form = LabForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        lab = form.save(commit=False)
        if department:
            lab.department = department
        lab.save()
        messages.success(request, 'Lab added successfully.')
        if department:
            return redirect('department_detail', pk=department.pk)
        return redirect('lab_list')
    return render(request, 'labs/lab_form.html', {'form': form, 'title': 'Add Lab', 'department': department})


@login_required
def department_list(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    departments = Department.objects.all().order_by('name')
    return render(request, 'labs/department_list.html', {'departments': departments})


@login_required
def add_department(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    form = DepartmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Department added successfully.')
        return redirect('department_list')
    return render(request, 'labs/department_form.html', {'form': form, 'title': 'Add Department'})


@login_required
def department_detail(request, pk):
    lab = get_object_or_404(Department, pk=pk)
    labs = lab.labs.all()
    return render(request, 'labs/department_detail.html', {'department': lab, 'labs': labs})


@login_required
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('department_list')

    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Department updated.')
        return redirect('department_detail', pk=pk)
    return render(request, 'labs/department_form.html', {'form': form, 'title': 'Edit Department'})


@login_required
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('department_list')

    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted.')
        return redirect('department_list')
    return render(request, 'labs/confirm_delete.html', {'object': department, 'title': 'Delete Department'})


@login_required
def lab_detail(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    status_filter = request.GET.get('status', 'working')
    search = request.GET.get('search', '')

    devices = lab.devices.all()
    if status_filter:
        devices = devices.filter(status=status_filter)
    if search:
        devices = devices.filter(Q(name__icontains=search) | Q(serial_id__icontains=search))

    alerts = Alert.objects.filter(lab=lab, is_dismissed=False)

    context = {
        'lab': lab,
        'devices': devices,
        'status_filter': status_filter,
        'search': search,
        'alerts': alerts,
        'active_count': lab.devices.filter(status='working').count(),
        'maintenance_count': lab.devices.filter(status='maintenance').count(),
        'trash_count': lab.devices.filter(status='trash').count(),
    }
    return render(request, 'labs/lab_detail.html', context)


@login_required
def edit_lab(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    form = LabForm(request.POST or None, instance=lab)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lab updated.')
        return redirect('lab_detail', pk=pk)
    return render(request, 'labs/lab_form.html', {'form': form, 'title': 'Edit Lab', 'lab': lab})


@login_required
def delete_lab(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    if request.method == 'POST':
        lab.delete()
        messages.success(request, 'Lab deleted.')
        return redirect('lab_list')
    return render(request, 'labs/confirm_delete.html', {'object': lab, 'title': 'Delete Lab'})


@login_required
def add_device(request, lab_pk):
    lab = get_object_or_404(Lab, pk=lab_pk)
    form = DeviceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        device = form.save(commit=False)
        device.lab = lab
        device.added_by = request.user
        device.save()
        DeviceHistory.objects.create(
            device=device,
            action='added',
            performed_by=request.user,
            notes=f'Device added to {lab.name}'
        )
        # Check threshold alert
        _check_alerts(device)
        messages.success(request, f'Device "{device.name}" added successfully.')
        return redirect('lab_detail', pk=lab_pk)
    return render(request, 'labs/device_form.html', {'form': form, 'lab': lab, 'title': 'Add Device'})


@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    history = device.history.select_related('performed_by').all()
    maintenance_requests = device.maintenance_requests.all()
    status_form = DeviceStatusForm(initial={'status': device.status})
    context = {
        'device': device,
        'history': history,
        'maintenance_requests': maintenance_requests,
        'status_form': status_form,
    }
    return render(request, 'labs/device_detail.html', context)


@login_required
def edit_device(request, pk):
    device = get_object_or_404(Device, pk=pk)
    form = DeviceForm(request.POST or None, instance=device)
    if request.method == 'POST' and form.is_valid():
        updated = form.save()
        DeviceHistory.objects.create(
            device=updated,
            action='updated',
            performed_by=request.user,
        )
        _check_alerts(updated)
        messages.success(request, 'Device updated.')
        return redirect('device_detail', pk=pk)
    return render(request, 'labs/device_form.html', {
        'form': form, 'lab': device.lab, 'title': 'Edit Device', 'device': device
    })


@login_required
def change_device_status(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        form = DeviceStatusForm(request.POST)
        if form.is_valid():
            old_status = device.status
            new_status = form.cleaned_data['status']
            notes = form.cleaned_data.get('notes', '')
            device.status = new_status
            device.save()

            action_map = {
                'maintenance': 'moved_maintenance',
                'working': 'returned_active',
                'trash': 'moved_trash',
            }
            DeviceHistory.objects.create(
                device=device,
                action=action_map.get(new_status, 'status_changed'),
                performed_by=request.user,
                old_value=old_status,
                new_value=new_status,
                notes=notes
            )
            _check_alerts(device)
            messages.success(request, f'Device status changed to {new_status}.')
    return redirect('device_detail', pk=pk)


@login_required
def delete_device(request, pk):
    device = get_object_or_404(Device, pk=pk)
    lab_pk = device.lab.pk
    if request.method == 'POST':
        device.delete()
        messages.success(request, 'Device deleted.')
        return redirect('lab_detail', pk=lab_pk)
    return render(request, 'labs/confirm_delete.html', {'object': device, 'title': 'Delete Device'})


@login_required
def category_list(request):
    categories = DeviceCategory.objects.annotate(device_count=Count('device'))
    return render(request, 'labs/category_list.html', {'categories': categories})


@login_required
def add_category(request):
    form = DeviceCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category added.')
        return redirect('category_list')
    return render(request, 'labs/category_form.html', {'form': form})


def _check_alerts(device):
    """Create alerts automatically based on device state."""
    # Maintenance alert
    if device.status == 'maintenance':
        Alert.objects.get_or_create(
            device=device,
            alert_type='maintenance',
            is_dismissed=False,
            defaults={
                'lab': device.lab,
                'message': f'{device.name} has been moved to maintenance.'
            }
        )
    # Trash alert
    if device.status == 'trash':
        Alert.objects.get_or_create(
            device=device,
            alert_type='trash',
            is_dismissed=False,
            defaults={
                'lab': device.lab,
                'message': f'{device.name} has been moved to trash.'
            }
        )