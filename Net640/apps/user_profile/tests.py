from django.test import TestCase
from Net640.apps.user_profile.models import User


class TestUserPermission(TestCase):
    def test_add_to_friends(self):
        user1 = User(username='iam1', email='iam1@m.ru')
        user1.save()

        user2 = User(username='iam2', email='iam2@m.ru')
        user2.save()

        user1.accept(user2)
        user2.accept(user1)

        assert user1.get_friends()[0].username == 'iam2'
        assert user2.get_friends()[0].username == 'iam1'
