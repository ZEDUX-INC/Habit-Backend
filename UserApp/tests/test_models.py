from django.test import TestCase
from UserApp.models import UserManager, UserAccount


class TestUserAccountManager(TestCase):

    def test_find_by_username_available(self)-> None:

        data =  {
            "username": "John",
            "first_name": "Nagni",
            "last_name": "Moni",
            "email": "example@example.com",
            "password": "WhenWeAllFallAsleep"
        }

        user = UserAccount.objects.create(**data)
        found = UserAccount.objects.find_by_username("John")[0]
        self.assertEqual(user, found, f"user {user} is not {found}")

    def test_find_by_username_unavailable(self) -> None:
        # test to assert that find_by_username return an empty queryset
        # when user is not available
        queryset =  UserAccount.objects.find_by_username("John")
        self.assertEqual(len(queryset), 0)




class TestUserAccount(TestCase):

    def test_email_label(self):
        pass

    def test_is_active_label(self):
        pass

    def test_email_is_required(self):
        pass