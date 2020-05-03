import os
import re
from uuid import uuid1

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail

from Net640.apps.user_profile.models import User
from Net640.testing.helpers import create_test_image
from Net640.httpcodes import HTTP_OK, HTTP_NOT_FOUND


class TestUserProfileViews(TestCase):
    def setUp(self):
        random_name = str(uuid1())
        self.user = User(username=random_name, email=random_name + '@m.ru', is_active=True)
        self.user.set_password('12345678')
        self.user.save()

        random_name = str(uuid1())
        self.friend = User(username=random_name, email=random_name + '@m.ru', is_active=True)
        self.friend.set_password('12345678')
        self.friend.save()

    def test_login_view(self):
        client = Client()
        response = client.post(reverse('user_profile:login'),
                               {'username': self.user.username, 'password': '12345678'}, follow=True)
        # check that user redirected to mainpage
        path, code = response.redirect_chain[0]
        self.assertEqual(path, '/')
        self.assertEqual(code, 302)
        # compare logged user with user in DB
        self.assertEqual(response.status_code, HTTP_OK)
        user_from_db = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_from_db.id, response.context['user'].id)

    def test_signup_view(self):
        random_name = str(uuid1())
        email_addr = random_name + '@m.ru'

        client = Client()
        response = client.post(reverse('user_profile:signup'), {'username': random_name,
                                                                'password': '12345678',
                                                                'password_again': '12345678',
                                                                'email': email_addr
                                                                }, follow=True)
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertIn(b'A confirmation code link has been sent to your email address.', response.content)
        # check email for activation code
        activation_mail = mail.outbox[-1]
        recipient_addr = activation_mail.to
        self.assertEqual(recipient_addr[0], email_addr)
        activation_link = re.search(r'\s(http[^\s]*)\s', activation_mail.body).group(1)
        activation_response = client.get(activation_link, follow=True)
        # check after activation
        self.assertEqual(activation_response.status_code, HTTP_OK)
        self.assertIn(b'<title>My page</title>', activation_response.content)

    def test_signup_view_when_confirmation_code_is_incorrect(self):
        random_name = str(uuid1())
        email_addr = random_name + '@m.ru'

        client = Client()
        response = client.post(reverse('user_profile:signup'), {'username': random_name,
                                                                'password': '12345678',
                                                                'password_again': '12345678',
                                                                'email': email_addr
                                                                }, follow=True)
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertIn(b'A confirmation code link has been sent to your email address.', response.content)
        # check email for activation code
        activation_mail = mail.outbox[-1]
        recipient_addr = activation_mail.to
        self.assertEqual(recipient_addr[0], email_addr)
        activation_link = re.search(r'\s(http[^\s]*)\s', activation_mail.body).group(1)
        activation_response = client.get(activation_link + 'wrong')
        # check after activation
        self.assertEqual(activation_response.status_code, HTTP_NOT_FOUND)

    def test_profile_view_when_update_existing_user(self):
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('user_profile:profile'), {'firstname': 'My First Name',
                                                                 'lastname': 'My Last Name',
                                                                 'patronymic': 'My Patronymic',
                                                                 'password': '87654321',
                                                                 'password_again': '87654321',
                                                                 })
        self.assertEqual(response.status_code, HTTP_OK)
        user_from_db = User.objects.get(username=self.user.username)
        self.assertEqual(user_from_db.firstname, 'My First Name')
        self.assertEqual(user_from_db.lastname, 'My Last Name')
        self.assertEqual(user_from_db.patronymic, 'My Patronymic')
        self.assertTrue(user_from_db.check_password('87654321'))

    def test_profile_remove_avatar(self):
        img_file, content_type = create_test_image()
        random_name = str(uuid1())
        email_addr = random_name + '@m.ru'

        user = User(username=random_name, email=email_addr,
                    avatar=SimpleUploadedFile('myimage.bmp', img_file.read(), content_type), is_active=True)
        user.set_password('12345678')
        user.save()
        # check before deletion
        self.assertTrue(os.path.exists(user.avatar.path))

        client = Client()
        client.login(username=user.username, password='12345678')
        response = client.post(reverse('user_profile:profile'), {'action': 'remove_avatar'})
        self.assertEqual(response.status_code, HTTP_OK)
        # check after deletion
        self.assertFalse(os.path.exists(user.avatar.path))

    def test_password_reset(self):
        client = Client()
        response = client.post(reverse('user_profile:reset_password'), {'email': self.user.email}, follow=True)
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertIn(b'We\'ve emailed you instructions for setting your password', response.content)
        # check email for reset code
        reset_request_mail = mail.outbox[-1]
        reset_link = re.search(r'\shttp:\/\/testserver([^\s]*)\s', reset_request_mail.body).group(1)
        reset_response = client.get(reset_link, follow=True)
        path, code = response.redirect_chain[0]
        # check after resetting password
        self.assertEqual(reset_response.status_code, HTTP_OK)
        response = client.post(reset_link, follow=True)
        self.assertNotContains(response, "The password reset link was invalid")
        # type new password
        upd_pass_link = response.redirect_chain[0][0]
        response = client.post(upd_pass_link, data={'password': 'qwertyuio', 'password_again': 'qwertyuio'})

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('12345678'))
        self.assertTrue(self.user.check_password('qwertyuio'))
        self.assertTrue(client.login(username=self.user.username, password='qwertyuio'))
