import json

from django.test import TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from clearance.models import ClearanceApprovalStatus, ClearanceRequestStatus, Office


def json_post(client, url, data, method="post"):
    return getattr(client, method)(url, data=json.dumps(data), content_type="application/json")


class ClearanceWorkflowTests(TestCase):
    def setUp(self):
        self.offices = [
            Office.objects.create(name="Adviser", slug="adviser", sign_order=1),
            Office.objects.create(name="Library", slug="library", sign_order=2),
        ]
        self.student = User.objects.create_user(
            email="student@demo.test", password="password", name="Juan", role=UserRole.STUDENT
        )
        self.approvers = [
            User.objects.create_user(
                email=f"{office.slug}@demo.test", password="password", name=office.name,
                role=UserRole.APPROVER, office=office,
            )
            for office in self.offices
        ]

    def test_student_can_submit_a_request_that_routes_to_every_office_in_order(self):
        self.client.force_login(self.student)
        response = json_post(self.client, reverse("student.clearance.store"), {"semester": "1st Sem"})
        self.assertRedirects(response, reverse("student.dashboard"))

        dashboard = self.client.get(reverse("student.dashboard"), headers={"x-inertia": "true", "x-inertia-version": "1.0"})
        clearance_request = dashboard.json()["props"]["clearanceRequest"]
        self.assertEqual(clearance_request["status"], ClearanceRequestStatus.PENDING)
        self.assertEqual([a["office"]["slug"] for a in clearance_request["approvals"]], ["adviser", "library"])

    def test_request_is_approved_only_once_every_office_signs(self):
        self.client.force_login(self.student)
        json_post(self.client, reverse("student.clearance.store"), {"semester": "1st Sem"})
        clearance_request = self.student.clearance_requests.first()
        first_approval, second_approval = clearance_request.approvals.order_by("office__sign_order")

        self.client.force_login(self.approvers[0])
        json_post(
            self.client, reverse("approver.approvals.update", args=[first_approval.id]),
            {"action": "sign", "signature_data": "data:image/png;base64,abc"}, method="patch",
        )
        clearance_request.refresh_from_db()
        self.assertEqual(clearance_request.status, ClearanceRequestStatus.PENDING)

        self.client.force_login(self.approvers[1])
        json_post(
            self.client, reverse("approver.approvals.update", args=[second_approval.id]),
            {"action": "sign", "signature_data": "data:image/png;base64,abc"}, method="patch",
        )
        clearance_request.refresh_from_db()
        self.assertEqual(clearance_request.status, ClearanceRequestStatus.APPROVED)
        self.assertIsNotNone(clearance_request.completed_at)

    def test_rejection_blocks_approval_until_resubmitted(self):
        self.client.force_login(self.student)
        json_post(self.client, reverse("student.clearance.store"), {"semester": "1st Sem"})
        clearance_request = self.student.clearance_requests.first()
        first_approval = clearance_request.approvals.order_by("office__sign_order").first()

        self.client.force_login(self.approvers[0])
        json_post(
            self.client, reverse("approver.approvals.update", args=[first_approval.id]),
            {"action": "reject", "remarks": "Missing document"}, method="patch",
        )
        clearance_request.refresh_from_db()
        self.assertEqual(clearance_request.status, ClearanceRequestStatus.REJECTED)

        self.client.force_login(self.student)
        json_post(self.client, reverse("student.approvals.resubmit", args=[first_approval.id]), {})
        first_approval.refresh_from_db()
        clearance_request.refresh_from_db()
        self.assertEqual(first_approval.status, ClearanceApprovalStatus.PENDING)
        self.assertEqual(clearance_request.status, ClearanceRequestStatus.PENDING)

    def test_approver_cannot_sign_off_for_a_different_office(self):
        self.client.force_login(self.student)
        json_post(self.client, reverse("student.clearance.store"), {"semester": "1st Sem"})
        clearance_request = self.student.clearance_requests.first()
        library_approval = clearance_request.approvals.get(office__slug="library")

        self.client.force_login(self.approvers[0])  # adviser approver
        response = self.client.get(reverse("approver.approvals.show", args=[library_approval.id]))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_approver_dashboard(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("approver.dashboard"))
        self.assertEqual(response.status_code, 403)
