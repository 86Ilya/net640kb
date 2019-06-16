from django.test import TestCase
from Net640.apps.user_profile.models import User
from Net640.apps.user_profile.models import RELATIONSHIP_FRIENDS, RELATIONSHIP_REQUEST_HAS_SENT
from Net640.apps.user_profile.models import RELATIONSHIP_WAITING_FOR_ACCEPT, NO_RELATIONSHIP


class TestUserPermission(TestCase):
    def test_send_request_for_relationship(self):
        user1 = User(username='test_send_request_for_relationship1', email='test_send_request_for_relationship1@m.ru')
        user1.save()

        user2 = User(username='test_send_request_for_relationship2', email='test_send_request_for_relationship2@m.ru')
        user2.save()

        user1.accept(user2)

        assert user1.check_relationship(user2) == RELATIONSHIP_REQUEST_HAS_SENT
        assert user2.check_relationship(user1) == RELATIONSHIP_WAITING_FOR_ACCEPT

    def test_cancel_own_send_request_for_relationship(self):
        user1 = User(username='test_cancel_send_request_for_relationship1',
                     email='test_cancel_send_request_for_relationship1@m.ru')
        user1.save()

        user2 = User(username='test_cancel_send_request_for_relationship2',
                     email='test_cancel_send_request_for_relationship2@m.ru')
        user2.save()

        user1.accept(user2)

        assert user1.check_relationship(user2) == RELATIONSHIP_REQUEST_HAS_SENT
        assert user2.check_relationship(user1) == RELATIONSHIP_WAITING_FOR_ACCEPT

        user1.cancel(user2)

        assert user1.check_relationship(user2) == NO_RELATIONSHIP
        assert user2.check_relationship(user1) == NO_RELATIONSHIP

    def test_cancel_foreign_send_request_for_relationship(self):
        user1 = User(username='test_cancel_foreign_send_request_for_relationship1',
                     email='test_cancel_foreign_send_request_for_relationship1@m.ru')
        user1.save()

        user2 = User(username='test_cancel_foreign_send_request_for_relationship2',
                     email='test_cancel_foreign_send_request_for_relationship2@m.ru')
        user2.save()

        user1.accept(user2)

        assert user1.check_relationship(user2) == RELATIONSHIP_REQUEST_HAS_SENT
        assert user2.check_relationship(user1) == RELATIONSHIP_WAITING_FOR_ACCEPT

        user2.cancel(user1)

        assert user1.check_relationship(user2) == NO_RELATIONSHIP
        assert user2.check_relationship(user1) == NO_RELATIONSHIP

    def test_add_to_friends(self):
        user1 = User(username='test_add_to_friends1', email='test_add_to_friends1@m.ru')
        user1.save()

        user2 = User(username='test_add_to_friends2', email='test_add_to_friends2@m.ru')
        user2.save()

        user1.accept(user2)
        user2.accept(user1)

        assert user1.check_relationship(user2) == RELATIONSHIP_FRIENDS
        assert user2.check_relationship(user1) == RELATIONSHIP_FRIENDS

        assert user1.get_friends()[0].username == 'test_add_to_friends2'
        assert user2.get_friends()[0].username == 'test_add_to_friends1'

    def test_remove_from_friends(self):
        user1 = User(username='test_remove_from_friends1', email='test_remove_from_friends1@m.ru')
        user1.save()

        user2 = User(username='test_remove_from_friends2', email='test_remove_from_friends2@m.ru')
        user2.save()

        user1.accept(user2)
        user2.accept(user1)

        user1.cancel(user2)

        assert user1.check_relationship(user2) == NO_RELATIONSHIP
        assert user2.check_relationship(user1) == NO_RELATIONSHIP
