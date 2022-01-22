"""
    Unit test file for models
"""
import pytest
from django.test import TestCase

from UserApp.models import CustomUser

pytestmark = pytest.mark.django_db

class UserModelTest(TestCase):
    """
    Test Model class
    """
    @classmethod
    def setUpTestData(cls):
        """
        :return: None
        """
        # Setting up objects which can be use for all test methods
        CustomUser.objects.create(
          email="example@gmail.com",
          username="Dev"
        )

    def test_user_email_label(self):
        """
          :return: None
        """
        user = CustomUser.objects.get(id=1)
        field_label = user._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'email address')