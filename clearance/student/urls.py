from django.urls import path

from clearance.student import views

urlpatterns = [
    path("dashboard", views.dashboard, name="student.dashboard"),
    path("clearance/create", views.create_request, name="student.clearance.create"),
    path("clearance", views.store_request, name="student.clearance.store"),
    path("clearance/<int:pk>", views.show_clearance, name="student.clearance.show"),
    path("approvals/<int:pk>/resubmit", views.resubmit, name="student.approvals.resubmit"),
]
