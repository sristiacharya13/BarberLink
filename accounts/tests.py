from django.test import TestCase
from rest_framework.test import APIClient

from barbers.models import Barber
from customers.models import Customer
from customers.serializers import CustomerSerializer

from .models import User


class CustomerSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            contact_number="9876500011", password="Str0ngPass!", role=User.ROLE_CUSTOMER
        )
        self.customer = Customer.objects.create(user=self.user, name="Joesph Lang")

    def test_returns_expected_keys(self):
        data = CustomerSerializer(self.customer).data
        self.assertEqual(set(data), {"customer_id", "name", "location"})

    def test_does_not_leak_user_fk(self):
        self.assertNotIn("user", CustomerSerializer(self.customer).data)


class DashboardApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.barber_user = User.objects.create_user(
            contact_number="9876500022", password="Str0ngPass!", role=User.ROLE_BARBER
        )
        self.barber = Barber.objects.create(user=self.barber_user, name="John Doe")

        self.customer_user = User.objects.create_user(
            contact_number="9876500033", password="Str0ngPass!", role=User.ROLE_CUSTOMER
        )
        Customer.objects.create(user=self.customer_user, name="Joesph Lang")

    def login(self, contact_number):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"contact_number": contact_number, "password": "Str0ngPass!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        return response.data

    def test_me_returns_name_and_role(self):
        self.login("9876500022")
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], "barber")
        self.assertEqual(response.data["name"], "John Doe")

    def test_anonymous_dashboard_data_is_rejected(self):
        self.assertEqual(self.client.get("/barbers/api/dashboard/").status_code, 401)
        self.assertEqual(self.client.get("/customers/api/dashboard/").status_code, 401)

    def test_barber_can_read_own_profile(self):
        self.login("9876500022")
        response = self.client.get("/barbers/api/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "John Doe")
        self.assertNotIn("user", response.data)

    def test_customer_can_read_own_profile(self):
        self.login("9876500033")
        response = self.client.get("/customers/api/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Joesph Lang")

    def test_roles_cannot_cross(self):
        self.login("9876500033")
        self.assertEqual(self.client.get("/barbers/api/dashboard/").status_code, 403)

        self.client.credentials()
        self.login("9876500022")
        self.assertEqual(self.client.get("/customers/api/dashboard/").status_code, 403)

    def test_logout_blacklists_refresh_token(self):
        tokens = self.login("9876500022")
        response = self.client.post(
            "/api/v1/auth/logout/", {"refresh": tokens["refresh"]}, format="json"
        )
        self.assertEqual(response.status_code, 205)

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"contact_number": "9876500022", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class RegisterApiTests(TestCase):
    def test_registration_creates_matching_profile(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "name": "Damien Ochoa",
                "contact_number": "98765 43210",
                "password": "Str0ngPass!",
                "role": "barber",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn("access", response.data)

        user = User.objects.get(contact_number="9876543210")
        self.assertEqual(user.role, "barber")
        self.assertTrue(Barber.objects.filter(user=user, name="Damien Ochoa").exists())

    def test_registration_rejects_invalid_phone(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "name": "Hubert Odonnell",
                "contact_number": "12345",
                "password": "Str0ngPass!",
                "role": "customer",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(contact_number="12345").exists())

    def test_registration_rejects_duplicate_phone(self):
        User.objects.create_user(contact_number="9876500099", password="Str0ngPass!")
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "name": "Someone",
                "contact_number": "9876500099",
                "password": "Str0ngPass!",
                "role": "customer",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)