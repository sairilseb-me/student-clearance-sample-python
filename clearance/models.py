from django.conf import settings
from django.db import models


class Office(models.Model):
    """An office a clearance request must be signed off by (e.g. Library, Treasurer)."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    sign_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sign_order"]

    def __str__(self):
        return self.name


class ClearanceRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class ClearanceApprovalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SIGNED = "signed", "Signed"
    REJECTED = "rejected", "Rejected"


class ClearanceRequest(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clearance_requests"
    )
    semester = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=ClearanceRequestStatus.choices, default=ClearanceRequestStatus.PENDING
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} — {self.semester}"

    def sync_status(self):
        """Recompute the overall status from the current state of the approvals.

        A single rejection blocks the whole request until the student has the
        rejecting office re-review it; the request is only approved once every
        office has signed.
        """
        approvals = list(self.approvals.all())

        if any(approval.status == ClearanceApprovalStatus.REJECTED for approval in approvals):
            self.status = ClearanceRequestStatus.REJECTED
            self.completed_at = None
        elif approvals and all(approval.status == ClearanceApprovalStatus.SIGNED for approval in approvals):
            from django.utils import timezone

            self.status = ClearanceRequestStatus.APPROVED
            self.completed_at = timezone.now()
        else:
            self.status = ClearanceRequestStatus.PENDING
            self.completed_at = None

        self.save(update_fields=["status", "completed_at", "updated_at"])


class ClearanceApproval(models.Model):
    clearance_request = models.ForeignKey(
        ClearanceRequest, on_delete=models.CASCADE, related_name="approvals"
    )
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="clearance_approvals")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="clearance_approvals",
    )
    status = models.CharField(
        max_length=20, choices=ClearanceApprovalStatus.choices, default=ClearanceApprovalStatus.PENDING
    )
    signed_at = models.DateTimeField(null=True, blank=True)
    signature_data = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.clearance_request} · {self.office}"
