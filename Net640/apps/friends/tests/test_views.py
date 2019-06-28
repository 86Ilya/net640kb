from uuid import uuid1

from django.test import TestCase, Client
from django.urls import reverse
from Net640.apps.user_profile.models import User
from Net640.apps.user_profile.models import RELATIONSHIP_FRIENDS, RELATIONSHIP_REQUEST_HAS_SENT
from Net640.apps.user_profile.models import RELATIONSHIP_WAITING_FOR_ACCEPT, NO_RELATIONSHIP


class TestFriendsView(TestCase):
    password = '12345678'

    def setUp(self):
        random_name = str(uuid1())
        self.user1 = User(username=random_name, email=random_name + '@m.ru')
        self.user1.set_password(self.password)
        self.user1.save()

        random_name = str(uuid1())
        self.user2 = User(username=random_name, email=random_name + '@m.ru')
        self.user2.set_password(self.password)
        self.user2.save()

    def test_view_send_request_for_relationship(self):
        client = Client()
        client.login(username=self.user1.username, password=self.password)
        response = client.post(reverse('user_view', kwargs={'user_id': self.user2.id}), {'action': 'add'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['relationship_status'], RELATIONSHIP_REQUEST_HAS_SENT)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_REQUEST_HAS_SENT)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_WAITING_FOR_ACCEPT)

    def test_view_cancel_own_send_request_for_relationship(self):
        client = Client()
        client.login(username=self.user1.username, password=self.password)
        response = client.post(reverse('user_view', kwargs={'user_id': self.user2.id}), {'action': 'add'})
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_REQUEST_HAS_SENT)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_WAITING_FOR_ACCEPT)

        response = client.post(reverse('friends'), {'action': 'cancel', 'user_id': self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['relationship_status'], NO_RELATIONSHIP)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), NO_RELATIONSHIP)
        self.assertEqual(self.user2.check_relationship(self.user1), NO_RELATIONSHIP)

    def test_view_cancel_foreign_send_request_for_relationship(self):
        client = Client()
        client.login(username=self.user1.username, password=self.password)
        response = client.post(reverse('user_view', kwargs={'user_id': self.user2.id}), {'action': 'add'})
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_REQUEST_HAS_SENT)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_WAITING_FOR_ACCEPT)

        client.login(username=self.user2.username, password=self.password)
        response = client.post(reverse('friends'), {'action': 'cancel', 'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['relationship_status'], NO_RELATIONSHIP)

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), NO_RELATIONSHIP)
        self.assertEqual(self.user2.check_relationship(self.user1), NO_RELATIONSHIP)

    def test_add_to_friends(self):
        client = Client()
        client.login(username=self.user1.username, password=self.password)
        response = client.post(reverse('user_view', kwargs={'user_id': self.user2.id}), {'action': 'add'})
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_REQUEST_HAS_SENT)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_WAITING_FOR_ACCEPT)

        client.login(username=self.user2.username, password=self.password)
        response = client.post(reverse('friends'), {'action': 'accept', 'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['relationship_status'], RELATIONSHIP_FRIENDS)

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_FRIENDS)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_FRIENDS)

        self.assertEqual(self.user1.get_friends()[0].username, self.user2.username)
        self.assertEqual(self.user2.get_friends()[0].username, self.user1.username)

    def test_remove_from_friends(self):
        client = Client()
        client.login(username=self.user1.username, password=self.password)
        response = client.post(reverse('user_view', kwargs={'user_id': self.user2.id}), {'action': 'add'})
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_REQUEST_HAS_SENT)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_WAITING_FOR_ACCEPT)

        client.login(username=self.user2.username, password=self.password)
        response = client.post(reverse('friends'), {'action': 'accept', 'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['relationship_status'], RELATIONSHIP_FRIENDS)

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), RELATIONSHIP_FRIENDS)
        self.assertEqual(self.user2.check_relationship(self.user1), RELATIONSHIP_FRIENDS)

        response = client.post(reverse('friends'), {'action': 'cancel', 'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['relationship_status'], NO_RELATIONSHIP)

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()

        self.assertEqual(self.user1.check_relationship(self.user2), NO_RELATIONSHIP)
        self.assertEqual(self.user2.check_relationship(self.user1), NO_RELATIONSHIP)
