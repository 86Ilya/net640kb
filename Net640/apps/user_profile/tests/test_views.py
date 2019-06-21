import os
from uuid import uuid1

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from Net640.apps.user_profile.models import User
from Net640.testing.helpers import create_test_image


class TestUserProfileViews(TestCase):
    def setUp(self):
        random_name = str(uuid1())
        self.user = User(username=random_name, email=random_name + '@m.ru')
        self.user.set_password('12345678')
        self.user.save()

        random_name = str(uuid1())
        self.friend = User(username=random_name, email=random_name + '@m.ru')
        self.friend.set_password('12345678')
        self.friend.save()

    def test_login_view(self):
        client = Client()
        response = client.post(reverse('login'), {'username': self.user.username, 'password': '12345678'}, follow=True)
        # check that user redirected to mainpage
        path, code = response.redirect_chain[0]
        self.assertEqual(path, '/')
        self.assertEqual(code, 302)
        # compare logged user with user in DB
        self.assertEqual(response.status_code, 200)
        user_from_db = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_from_db.id, response.context['user'].id)

    def test_signup_view(self):
        random_name = str(uuid1())

        client = Client()
        response = client.post(reverse('signup'), {'username': random_name,
                                                   'password': '12345678',
                                                   'password_again': '12345678',
                                                   'email': random_name + '@m.ru',
                                                   }, follow=True)
        # check that user redirected to mainpage
        path, code = response.redirect_chain[0]
        self.assertEqual(path, '/')
        self.assertEqual(code, 302)
        # compare logged user with user in DB
        self.assertEqual(response.status_code, 200)
        user_from_db = User.objects.get(username=random_name)
        self.assertEqual(user_from_db.id, response.context['user'].id)

    def test_profile_view_when_update_existing_user(self):
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('profile'), {'firstname': 'My First Name',
                                                    'lastname': 'My Last Name',
                                                    'patronymic': 'My Patronymic',
                                                    'password': '87654321',
                                                    'password_again': '87654321',
                                                    })
        self.assertEqual(response.status_code, 200)
        user_from_db = User.objects.get(username=self.user.username)
        self.assertEqual(user_from_db.firstname, 'My First Name')
        self.assertEqual(user_from_db.lastname, 'My Last Name')
        self.assertEqual(user_from_db.patronymic, 'My Patronymic')
        self.assertTrue(user_from_db.check_password('87654321'))

    def test_profile_remove_avatar(self):
        img_file, content_type = create_test_image()
        random_name = str(uuid1())

        user = User(username=random_name, email=random_name + '@m.ru',
                    avatar=SimpleUploadedFile('myimage.bmp', img_file.read(), content_type))
        user.set_password('12345678')
        user.save()
        # check before deletion
        self.assertTrue(os.path.exists(user.avatar.path))

        client = Client()
        client.login(username=user.username, password='12345678')
        response = client.post(reverse('profile'), {'action': 'remove_avatar'})
        self.assertEqual(response.status_code, 200)
        # check after deletion
        self.assertFalse(os.path.exists(user.avatar.path))
