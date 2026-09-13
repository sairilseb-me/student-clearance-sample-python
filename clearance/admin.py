from django.contrib import admin

from clearance.models import ClearanceApproval, ClearanceRequest, Office


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "sign_order"]
    ordering = ["sign_order"]


class ClearanceApprovalInline(admin.TabularInline):
    model = ClearanceApproval
    extra = 0
    fields = ["office", "approver", "status", "signed_at", "remarks"]
    readonly_fields = ["signed_at"]


@admin.register(ClearanceRequest)
class ClearanceRequestAdmin(admin.ModelAdmin):
    list_display = ["student", "semester", "status", "completed_at"]
    list_filter = ["status"]
    inlines = [ClearanceApprovalInline]


@admin.register(ClearanceApproval)
class ClearanceApprovalAdmin(admin.ModelAdmin):
    list_display = ["clearance_request", "office", "approver", "status", "signed_at"]
    list_filter = ["status", "office"]
