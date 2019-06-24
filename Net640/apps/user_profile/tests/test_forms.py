from uuid import uuid1

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from Net640.apps.user_profile.forms import UserForm
from Net640.testing.helpers import create_test_image


class TestUserProfileForms(TestCase):
    def setUp(self):
        self.random_name = str(uuid1())
        self.email = self.random_name + '@m.ru'
        self.password = '12345678'

    def test_user_form(self):
        img_file, content_type = create_test_image()
        avatar = SimpleUploadedFile('myavatar.bmp', img_file.read(), content_type)
        user_form_data = {'username': self.random_name,
                          'email': self.email,
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data, {'avatar': avatar})
        self.assertTrue(user_form.is_valid())

    def test_user_from_when_username_is_too_long(self):
        name = 'X' * 121
        user_form_data = {'username': name,
                          'email': self.email,
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data)
        with self.assertRaises(KeyError):
            user_form.is_valid()
        self.assertIn('Ensure this value has at most 120 characters', user_form.errors['username'][0])

    def test_user_from_when_username_is_too_short(self):
        name = 'XX'
        user_form_data = {'username': name,
                          'email': self.email,
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data)
        with self.assertRaises(KeyError):
            user_form.is_valid()
        self.assertIn('Ensure this value has at least 3 characters', user_form.errors['username'][0])

    def test_user_from_when_username_had_wrong_symbols(self):
        name = 'X.X'
        user_form_data = {'username': name,
                          'email': self.email,
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data)
        with self.assertRaises(KeyError):
            user_form.is_valid()
        self.assertIn('Username should contain only letters, digits, underscores, and dashes',
                      user_form.errors['username'][0])

    def test_user_from_when_email_is_incorrect(self):
        user_form_data = {'username': self.random_name,
                          'email': self.random_name + 'm.ru',
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data)
        with self.assertRaises(KeyError):
            user_form.is_valid()
        self.assertEqual(user_form.errors['email'][0], 'Enter a valid email address.')

    def test_user_form_when_password_is_incorrect(self):
        user_form_data = {'username': self.random_name,
                          'email': self.email,
                          'password': '123456789',
                          'password_again': '12345678',
                          }
        user_form = UserForm(user_form_data)
        self.assertFalse(user_form.is_valid())
        self.assertEqual(user_form.errors['__all__'][0], 'Passwords mismatch')

    def test_user_from_when_avatar_is_too_large(self):
        img_file, content_type = create_test_image(3000)
        avatar = SimpleUploadedFile('myavatar.bmp', img_file.read(), content_type)
        user_form_data = {'username': self.random_name,
                          'email': self.email,
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data, {'avatar': avatar})
        self.assertFalse(user_form.is_valid())
        self.assertEqual(user_form.errors['__all__'][0], 'You have only 640Kb for all purposes!')
