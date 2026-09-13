import json


def inertia_data(request):
    """Parse the JSON body Inertia sends for POST/PATCH/PUT visits.

    Inertia serializes form data as JSON unless the payload contains a File,
    so request.POST (which only understands form-encoded/multipart bodies)
    is not enough for PATCH/PUT requests or JSON POSTs.
    """
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode())
    except (ValueError, UnicodeDecodeError):
        return {}
