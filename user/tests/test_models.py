from django.contrib.auth import get_user_model
from django.test import TestCase

from user.models import User


def test_user(**params) -> User:
    defaults = {
        "username": "test_username",
        "email": "test@test.com",
        "first_name": "test_first_name",
        "last_name": "test_last_name",
    }
    defaults.update(**params)
    return get_user_model().objects.create_user(**defaults)


class ModelsTests(TestCase):
    def test_user_str_with_bio(self) -> None:
        password = "test1234"
        bio = "test biography"
        user = test_user(password=password, bio=bio)

        self.assertEquals(user.bio, bio)
        self.assertTrue(user.check_password(password))
        self.assertEquals(str(user), f"{user.first_name} {user.last_name}")
