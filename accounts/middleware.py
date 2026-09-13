from inertia import share


class InertiaShareMiddleware:
    """Shares data with every Inertia page, mirroring Laravel's HandleInertiaRequests.

    - `auth.user`: the logged-in user (id/name/email/role/office_id), or None.
    - `errors`: validation errors flashed to the session by the previous
      request, popped so they only surface once (mirrors Laravel/Inertia's
      "redirect back with errors" convention).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        share(
            request,
            auth={"user": lambda: request.user.to_props() if request.user.is_authenticated else None},
            errors=request.session.pop("_inertia_errors", {}),
        )
        return self.get_response(request)


def flash_errors(request, errors):
    request.session["_inertia_errors"] = errors
