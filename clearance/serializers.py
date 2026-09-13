def serialize_office(office):
    return {
        "id": office.id,
        "name": office.name,
        "slug": office.slug,
        "sign_order": office.sign_order,
    }


def serialize_user(user):
    if user is None:
        return None
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "office_id": user.office_id,
    }


def serialize_approval(approval, *, with_clearance_request=False):
    data = {
        "id": approval.id,
        "clearance_request_id": approval.clearance_request_id,
        "office_id": approval.office_id,
        "approver_id": approval.approver_id,
        "status": approval.status,
        "signed_at": approval.signed_at,
        "signature_data": approval.signature_data,
        "remarks": approval.remarks,
        "office": serialize_office(approval.office),
        "approver": serialize_user(approval.approver),
    }
    if with_clearance_request:
        data["clearance_request"] = serialize_clearance_request(approval.clearance_request, with_student=True)
    return data


def serialize_clearance_request(clearance_request, *, with_student=False, with_approvals=False):
    data = {
        "id": clearance_request.id,
        "student_id": clearance_request.student_id,
        "semester": clearance_request.semester,
        "status": clearance_request.status,
        "completed_at": clearance_request.completed_at,
    }
    if with_student:
        data["student"] = serialize_user(clearance_request.student)
    if with_approvals:
        data["approvals"] = [
            serialize_approval(approval)
            for approval in clearance_request.approvals.select_related("office", "approver").all()
        ]
    return data


def serialize_pending_approval(approval):
    return {
        "id": approval.id,
        "status": approval.status,
        "clearance_request": serialize_clearance_request(approval.clearance_request, with_student=True),
    }
