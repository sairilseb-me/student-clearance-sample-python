from django.urls import path

from assistant import views

urlpatterns = [
    path("status", views.status, name="assistant.status"),
    path("chat", views.chat, name="assistant.chat"),
]
