from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from inertia import render

from accounts.decorators import role_required
from accounts.middleware import flash_errors
from accounts.models import UserRole
from clearance.models import ClearanceApproval, ClearanceApprovalStatus, ClearanceRequest, ClearanceRequestStatus, Office
from clearance.serializers import serialize_clearance_request, serialize_office
from core.http import inertia_data


@role_required(UserRole.STUDENT)
def dashboard(request):
    clearance_request = (
        request.user.clearance_requests.prefetch_related("approvals__office", "approvals__approver")
        .order_by("-created_at")
        .first()
    )

    return render(
        request,
        "Student/Dashboard",
        props={
            "clearanceRequest": serialize_clearance_request(clearance_request, with_approvals=True)
            if clearance_request
            else None,
        },
    )


@role_required(UserRole.STUDENT)
@require_http_methods(["GET"])
def create_request(request):
    offices = Office.objects.order_by("sign_order")
    return render(
        request,
        "Student/SubmitRequest",
        props={"offices": [serialize_office(office) for office in offices]},
    )


@role_required(UserRole.STUDENT)
@require_http_methods(["POST"])
def store_request(request):
    has_active_request = request.user.clearance_requests.filter(
        status__in=[ClearanceRequestStatus.PENDING, ClearanceRequestStatus.REJECTED]
    ).exists()
    if has_active_request:
        raise PermissionDenied(
            "You already have an active clearance request. If it was rejected, "
            "request a resubmission instead of starting a new one."
        )

    data = inertia_data(request)
    semester = (data.get("semester") or "").strip()

    if not semester:
        flash_errors(request, {"semester": "The semester field is required."})
        return redirect("student.clearance.create")

    clearance_request = ClearanceRequest.objects.create(student=request.user, semester=semester)
    for office in Office.objects.order_by("sign_order"):
        ClearanceApproval.objects.create(
            clearance_request=clearance_request,
            office=office,
            status=ClearanceApprovalStatus.PENDING,
        )

    return redirect("student.dashboard")


@role_required(UserRole.STUDENT)
def show_clearance(request, pk):
    clearance_request = get_object_or_404(
        ClearanceRequest.objects.prefetch_related("approvals__office", "approvals__approver"), pk=pk
    )
    _authorize_ownership(request, clearance_request)

    return render(
        request,
        "Student/ClearancePdf",
        props={"clearanceRequest": serialize_clearance_request(clearance_request, with_student=True, with_approvals=True)},
    )


@role_required(UserRole.STUDENT)
@require_http_methods(["POST"])
def resubmit(request, pk):
    approval = get_object_or_404(ClearanceApproval, pk=pk)
    clearance_request = approval.clearance_request
    _authorize_ownership(request, clearance_request)

    if approval.status != ClearanceApprovalStatus.REJECTED:
        raise PermissionDenied

    approval.status = ClearanceApprovalStatus.PENDING
    approval.approver = None
    approval.signed_at = None
    approval.signature_data = None
    approval.remarks = None
    approval.save()

    clearance_request.sync_status()

    return redirect("student.dashboard")


def _authorize_ownership(request, clearance_request):
    if clearance_request.student_id != request.user.id:
        raise PermissionDenied
