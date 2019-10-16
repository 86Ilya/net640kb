from uuid import uuid1

from django.core.cache import cache
from django.test import TestCase
from Net640.apps.user_profile.models import User
from Net640.apps.user_profile.models import RELATIONSHIP_FRIENDS, RELATIONSHIP_REQUEST_HAS_SENT
from Net640.apps.user_profile.models import RELATIONSHIP_WAITING_FOR_ACCEPT, NO_RELATIONSHIP


class TestUserPermission(TestCase):
    def setUp(self):
        random_name = str(uuid1())
        self.user1 = User(username=random_name, email=random_name + '@m.ru')
        self.user1.set_password('12345678')
        self.user1.save()

        random_name = str(uuid1())
        self.user2 = User(username=random_name, email=random_name + '@m.ru')
        self.user2.set_password('12345678')
        self.user2.save()

    def test_send_request_for_relationship(self):
        self.user1.accept(self.user2)

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_REQUEST_HAS_SENT)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_WAITING_FOR_ACCEPT)

    def test_cancel_own_send_request_for_relationship(self):
        self.user1.accept(self.user2)

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_REQUEST_HAS_SENT)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_WAITING_FOR_ACCEPT)

        self.user1.cancel(self.user2)

        self.assertEqual(self.user1.check_relationship(self.user2), NO_RELATIONSHIP)
        self.assertEqual(self.user2.check_relationship(self.user1), NO_RELATIONSHIP)

    def test_cancel_foreign_send_request_for_relationship(self):
        self.user1.accept(self.user2)

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_REQUEST_HAS_SENT)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_WAITING_FOR_ACCEPT)

        self.user2.cancel(self.user1)

        self.assertEqual(self.user1.check_relationship(self.user2), NO_RELATIONSHIP)
        self.assertEqual(self.user2.check_relationship(self.user1), NO_RELATIONSHIP)

    def test_add_to_friends(self):
        self.user1.accept(self.user2)
        self.user2.accept(self.user1)

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_FRIENDS)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_FRIENDS)

        self.assertEqual(self.user1.get_friends()[0].username, self.user2.username)
        self.assertEqual(self.user2.get_friends()[0].username, self.user1.username)

    def test_remove_from_friends(self):
        self.user1.accept(self.user2)
        self.user2.accept(self.user1)

        self.user1.cancel(self.user2)

        self.assertEqual(self.user1.check_relationship(self.user2), NO_RELATIONSHIP)
        self.assertEqual(self.user2.check_relationship(self.user1), NO_RELATIONSHIP)


class TestCaching(TestCase):
    def setUp(self):
        random_name = str(uuid1())
        self.user1 = User(username=random_name, email=random_name + '@m.ru')
        self.user1.set_password('12345678')
        self.user1.save()

    def test_get_size_caching_is_working(self):
        fake_size = 777
        cache.delete(self.user1.id)

        size = self.user1.get_size()
        cache.set(self.user1.id, fake_size)

        self.assertNotEqual(size, fake_size)
        self.assertEqual(fake_size, self.user1.get_size())
