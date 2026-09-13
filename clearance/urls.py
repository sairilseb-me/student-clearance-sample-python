from django.urls import include, path

urlpatterns = [
    path("student/", include("clearance.student.urls")),
    path("approver/", include("clearance.approver.urls")),
]
