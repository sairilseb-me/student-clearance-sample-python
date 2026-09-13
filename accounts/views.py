from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from inertia import render

from accounts.middleware import flash_errors
from accounts.models import UserRole
from core.http import inertia_data


def redirect_path_for(role):
    if role == UserRole.APPROVER:
        return "approver.dashboard"
    return "student.dashboard"


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(redirect_path_for(request.user.role))

    if request.method == "GET":
        return render(request, "Auth/Login", props={})

    data = inertia_data(request)
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    errors = {}
    if not email:
        errors["email"] = "The email field is required."
    if not password:
        errors["password"] = "The password field is required."

    user = None
    if not errors:
        user = authenticate(request, username=email, password=password)
        if user is None:
            errors["email"] = "These credentials do not match our records."

    if errors:
        flash_errors(request, errors)
        return redirect("login")

    login(request, user)
    return redirect(redirect_path_for(user.role))


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect("login")
