import json

from django.test import TestCase
from django.urls import reverse

from accounts.models import User, UserRole


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="student@demo.test", password="password", name="Juan", role=UserRole.STUDENT)

    def test_valid_credentials_log_the_user_in_and_redirect_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            data=json.dumps({"email": "student@demo.test", "password": "password"}),
            content_type="application/json",
        )
        self.assertRedirects(response, reverse("student.dashboard"))

    def test_invalid_credentials_flash_an_error_and_do_not_log_in(self):
        response = self.client.post(
            reverse("login"),
            data=json.dumps({"email": "student@demo.test", "password": "wrong"}),
            content_type="application/json",
        )
        self.assertRedirects(response, reverse("login"))
        self.assertFalse(response.wsgi_request.session.get("_auth_user_id"))

    def test_authenticated_user_visiting_login_is_redirected_to_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("student.dashboard"))
