from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User
from user.serializers import UserListSerializer, UserDetailSerializer

USER_URL = reverse("user:user-list")
USER_UPDATE_URL = reverse("user:manage")
USER_ACTIVITY_URL = reverse("user:activity")


def test_user(**params) -> User:
    defaults = {
        "username": "test_username",
        "email": "test@test.com",
        "password": "test1234",
        "first_name": "test_first_name",
        "last_name": "test_last_name",
    }
    defaults.update(**params)
    return get_user_model().objects.create_user(**defaults)


def detail_url(user_id: int):
    return reverse_lazy("user:user-detail", args=[user_id])


class UnauthenticatedUserApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(USER_UPDATE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="user_username",
            email="user@test.com",
            password="user1234",
            first_name="user_first_name",
            last_name="user_last_name",
        )
        self.client.force_authenticate(self.user)
        self.user.last_login = timezone.now()

    def test_list_users(self) -> None:
        test_user()
        test_user(username="spider", email="test2@test.com")
        users = get_user_model().objects.all()
        serializer = UserListSerializer(users, many=True)

        response = self.client.get(USER_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_by_username(self) -> None:
        user1 = test_user()
        user2 = test_user(username="spider", email="test2@test.com")
        serializer1 = UserListSerializer(user1)
        serializer2 = UserListSerializer(user2)

        response = self.client.get(USER_URL, {"username": "spider"})

        self.assertNotIn(serializer1.data, response.data["results"])
        self.assertIn(serializer2.data, response.data["results"])

    def test_filter_by_first_name(self) -> None:
        user1 = test_user()
        user2 = test_user(
            username="spider", email="test2@test.com", first_name="Bob"
        )
        serializer1 = UserListSerializer(user1)
        serializer2 = UserListSerializer(user2)

        response = self.client.get(USER_URL, {"first_name": "bob"})

        self.assertNotIn(serializer1.data, response.data["results"])
        self.assertIn(serializer2.data, response.data["results"])

    def test_filter_by_last_name(self) -> None:
        user1 = test_user()
        user2 = test_user(
            username="spider", email="test2@test.com", last_name="Brown"
        )
        serializer1 = UserListSerializer(user1)
        serializer2 = UserListSerializer(user2)

        response = self.client.get(USER_URL, {"last_name": "bro"})

        self.assertNotIn(serializer1.data, response.data["results"])
        self.assertIn(serializer2.data, response.data["results"])

    def test_retrieve_user(self) -> None:
        user = test_user()
        url = detail_url(user.id)
        serializer = UserDetailSerializer(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_user(self) -> None:
        payload = {"bio": "user's biography"}
        url = detail_url(self.user.id)

        response1 = self.client.patch(USER_UPDATE_URL, payload)
        response2 = self.client.get(url)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["bio"], payload["bio"])

    def test_delete_user_forbidden(self) -> None:
        user = test_user()
        url = detail_url(user.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_last_login(self) -> None:
        last_login = self.user.last_login

        response = self.client.get(USER_ACTIVITY_URL)

        self.assertEqual(
            response.data["user_username's last login"], last_login
        )


class AdminMovieSessionApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "admin1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_delete_user(self) -> None:
        user = test_user()
        url = detail_url(user.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
