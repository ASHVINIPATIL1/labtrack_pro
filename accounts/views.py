from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import LoginForm, AddUserForm, EditUserForm
from .models import UserProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            # Create profile if missing (for superuser)
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'admin'})
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def user_list(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    users = User.objects.select_related('profile').all().order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def add_user(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    form = AddUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User created successfully.')
        return redirect('user_list')
    
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Add User'})


@login_required
def edit_user(request, pk):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    form = EditUserForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated successfully.')
        return redirect('user_list')
    
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Edit User'})


@login_required
def delete_user(request, pk):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted.')
        return redirect('user_list')
    
    return render(request, 'accounts/confirm_delete.html', {'object': user, 'title': 'Delete User'})