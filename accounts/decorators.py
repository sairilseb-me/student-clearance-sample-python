from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(role):
    """Mirrors Laravel's EnsureUserHasRole middleware: the user must hold the
    given role, or be an admin (admins can access any role-gated view)."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated or (user.role != role and not user.is_admin()):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
