from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class ConfirmationPagesTests(TestCase):
    """Ensure auth / confirmation related pages render correctly with CSS."""

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password",
            user_type="jobseeker",
        )

    def assertBaseTemplate(self, response):
        """Helper to assert our base layout is part of template list and CSS link exists."""
        # Template inheritance
        templates = [t.name for t in response.templates if t.name]
        self.assertIn("base.html", templates)
        # Ensure static CSS file link present
        self.assertContains(response, "static/css/style.css")

    def test_email_confirmation_sent_page(self):
        url = reverse("account_email_verification_sent")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertBaseTemplate(response)

    def test_email_confirm_with_invalid_key(self):
        # using a dummy key so page renders invalid link message
        url = reverse("account_confirm_email", kwargs={"key": "invalid-key"})
        response = self.client.get(url)
        # The view returns 200 with template because key is parsed but invalid
        self.assertEqual(response.status_code, 200)
        self.assertBaseTemplate(response)
        self.assertContains(response, "invalid")

    def test_password_reset_pages_flow(self):
        # initiate reset to generate session
        self.client.post(reverse("account_reset_password"), {"email": self.user.email})

        # password reset done page
        url_done = reverse("account_reset_password_done")
        response_done = self.client.get(url_done)
        self.assertEqual(response_done.status_code, 200)
        self.assertBaseTemplate(response_done)

        # We can't easily get valid uid/token without parsing email, but confirm template load can be
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        dummy_token = "set-password"
        url_confirm = reverse("account_reset_password_from_key", kwargs={"uidb64": uidb64, "key": dummy_token})
        response_confirm = self.client.get(url_confirm)
        # invalid token shows error page but still loads
        self.assertEqual(response_confirm.status_code, 200)
        self.assertBaseTemplate(response_confirm)
