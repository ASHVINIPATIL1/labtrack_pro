from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Alert


@login_required
def dismiss_alert(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    if request.method == 'POST':
        alert.is_dismissed = True
        alert.dismissed_by = request.user
        alert.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))