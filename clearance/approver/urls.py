from django.urls import path

from clearance.approver import views

urlpatterns = [
    path("dashboard", views.dashboard, name="approver.dashboard"),
    # Django resolves incoming requests by path only (not by method), so both
    # names point at the same pattern; `show_or_update` dispatches on
    # request.method internally. The `update` entry exists so `reverse()`
    # (and the JS route() shim) can resolve the PATCH route by its Laravel-
    # equivalent name, mirroring the original two-verbs-one-URI route pair.
    path("approvals/<int:pk>", views.show_or_update, name="approver.approvals.show"),
    path("approvals/<int:pk>", views.show_or_update, name="approver.approvals.update"),
]
