from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.models import UserRole


@login_required
def root(request):
    destination = "approver.dashboard" if request.user.role == UserRole.APPROVER else "student.dashboard"
    return redirect(destination)
