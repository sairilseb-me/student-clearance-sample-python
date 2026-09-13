from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from inertia import render

from accounts.decorators import role_required
from accounts.middleware import flash_errors
from accounts.models import UserRole
from clearance.models import ClearanceApproval, ClearanceApprovalStatus, ClearanceRequestStatus
from clearance.serializers import serialize_approval, serialize_pending_approval
from core.http import inertia_data


@role_required(UserRole.APPROVER)
def dashboard(request):
    pending_approvals = (
        request.user.office.clearance_approvals.select_related("clearance_request__student")
        .filter(status=ClearanceApprovalStatus.PENDING)
        .exclude(clearance_request__status=ClearanceRequestStatus.REJECTED)
        .order_by("-created_at")
    )

    return render(
        request,
        "Approver/Dashboard",
        props={"pendingApprovals": [serialize_pending_approval(approval) for approval in pending_approvals]},
    )


@role_required(UserRole.APPROVER)
@require_http_methods(["GET", "PATCH"])
def show_or_update(request, pk):
    approval = get_object_or_404(
        ClearanceApproval.objects.select_related("clearance_request__student", "office"), pk=pk
    )
    _authorize_office(request, approval)

    if request.method == "GET":
        return render(
            request,
            "Approver/SignOff",
            props={"clearanceApproval": serialize_approval(approval, with_clearance_request=True)},
        )

    data = inertia_data(request)
    action = data.get("action")
    signature_data = data.get("signature_data")
    remarks = data.get("remarks")

    errors = {}
    if action not in ("sign", "reject"):
        errors["action"] = "The action field must be either sign or reject."
    if action == "sign" and not signature_data:
        errors["signature_data"] = "The signature data field is required."

    if errors:
        flash_errors(request, errors)
        return redirect("approver.approvals.show", pk=pk)

    approval.status = ClearanceApprovalStatus.SIGNED if action == "sign" else ClearanceApprovalStatus.REJECTED
    approval.approver = request.user
    approval.signed_at = timezone.now()
    approval.signature_data = signature_data if action == "sign" else None
    approval.remarks = remarks or None
    approval.save()

    approval.clearance_request.sync_status()

    return redirect("approver.dashboard")


def _authorize_office(request, approval):
    if approval.office_id != request.user.office_id:
        raise PermissionDenied
