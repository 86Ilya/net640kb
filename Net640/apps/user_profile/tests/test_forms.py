from uuid import uuid1

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from Net640.apps.user_profile.models import User
from Net640.apps.user_profile.forms import UserForm, UserUpdateForm,\
    UserRequestPasswordResetForm, UserPasswordUpdateForm
from Net640.testing.helpers import create_test_image
from Net640.settings import DATE_FORMAT, MAX_PAGE_SIZE


class TestUserForm(TestCase):
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
        self.assertFalse(user_form.is_valid())
        self.assertIn('Ensure this value has at most 120 characters', user_form.errors['username'][0])

    def test_user_from_when_username_is_too_short(self):
        name = 'XX'
        user_form_data = {'username': name,
                          'email': self.email,
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data)
        self.assertFalse(user_form.is_valid())
        self.assertIn('Ensure this value has at least 3 characters', user_form.errors['username'][0])

    def test_user_from_when_username_had_wrong_symbols(self):
        name = 'X.X'
        user_form_data = {'username': name,
                          'email': self.email,
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data)
        self.assertFalse(user_form.is_valid())
        self.assertIn('Username should contain only letters, digits, underscores, and dashes',
                      user_form.errors['username'][0])

    def test_user_from_when_email_is_incorrect(self):
        user_form_data = {'username': self.random_name,
                          'email': self.random_name + 'm.ru',
                          'password': self.password,
                          'password_again': self.password,
                          }
        user_form = UserForm(user_form_data)
        self.assertFalse(user_form.is_valid())
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


class TestUserUpdateForm(TestCase):
    def setUp(self):
        random_name = str(uuid1())
        img_file, content_type = create_test_image()
        avatar = SimpleUploadedFile('myavatar.bmp', img_file.read(), content_type)

        self.user = User(username=random_name, email=random_name + '@m.ru', avatar=avatar)
        self.user.set_password('12345678')
        self.user.firstname = 'user firstname'
        self.user.lastname = 'user lastname'
        self.user.patronymic = 'user patronymic'
        self.user.birth_date = timezone.datetime(year=1986, month=4, day=10)
        self.user.save()

    def test_update_basic_user_text_data(self):
        newfirstname = 'new firstname'
        newlastname = 'new lastname'
        newpatronymic = 'new patronymic'
        newbirth_date = '10.04.1986'

        update_form = UserUpdateForm({'firstname': newfirstname,
                                      'lastname': newlastname,
                                      'patronymic': newpatronymic,
                                      'birth_date': newbirth_date},
                                     instance=self.user)
        self.assertTrue(update_form.is_valid())
        update_form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.firstname, newfirstname)
        self.assertEqual(self.user.lastname, newlastname)
        self.assertEqual(self.user.patronymic, newpatronymic)
        self.assertEqual(timezone.datetime.strftime(self.user.birth_date, DATE_FORMAT), newbirth_date)

    def test_update_user_avatar(self):
        img_file, content_type = create_test_image(100)
        avatar = {'avatar': SimpleUploadedFile('newavatar.bmp', img_file.read(), content_type)}
        update_form = UserUpdateForm({}, avatar, instance=self.user)
        self.assertTrue(update_form.is_valid())
        update_form.save()
        self.assertEqual(avatar['avatar'].size, update_form.cleaned_data['avatar'].size)
        self.assertEqual('newavatar.bmp', update_form.cleaned_data['avatar'].name)

    def test_update_user_avatar_when_pic_is_too_large(self):
        img_file, content_type = create_test_image(3000)
        avatar = {'avatar': SimpleUploadedFile('newavatar.bmp', img_file.read(), content_type)}
        update_form = UserUpdateForm({}, avatar, instance=self.user)
        self.assertFalse(update_form.is_valid())
        self.assertEqual(update_form.errors['__all__'][0], 'Not enough space')

    def test_update_user_password(self):
        newpass = 'qweasdzxc'
        update_form = UserUpdateForm({'password': newpass,
                                      'password_again': newpass},
                                     instance=self.user)
        self.assertTrue(update_form.is_valid())
        update_form.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(newpass))

    def test_update_user_password_when_passwords_are_differ(self):
        newpass = 'qweasdzxc'
        update_form = UserUpdateForm({'password': newpass,
                                      'password_again': newpass + "occasional symbols"},
                                     instance=self.user)
        self.assertFalse(update_form.is_valid())
        self.assertEqual(update_form.errors['__all__'][0], 'Passwords mismatch')

    def test_update_user_password_when_password_is_short(self):
        newpass = 'x' * 7
        update_form = UserUpdateForm({'password': newpass,
                                      'password_again': newpass},
                                     instance=self.user)
        self.assertFalse(update_form.is_valid())
        self.assertEqual(update_form.errors['__all__'][0], 'Password length must be at least 8 symbols')

    def test_update_user_password_when_password_is_too_large(self):
        newpass = 'x' * (MAX_PAGE_SIZE + 1)
        update_form = UserUpdateForm({'password': newpass,
                                      'password_again': newpass},
                                     instance=self.user)
        self.assertFalse(update_form.is_valid())
        self.assertEqual(update_form.errors['__all__'][0], 'You have only 640Kb for all purposes!')


class TestUserRequestPasswordResetForm(TestCase):

    def test_request_password_reset_form_when_email_is_correct(self):
        email = "xxx@m.ru"
        reset_form = UserRequestPasswordResetForm({'email': email})
        self.assertTrue(reset_form.is_valid())

    def test_request_password_reset_form_when_email_is_too_long(self):
        email = 'X' * 250 + "@m.ru"
        reset_form = UserRequestPasswordResetForm({'email': email})
        self.assertFalse(reset_form.is_valid())
        self.assertIn('Ensure this value has at most 254 characters', reset_form.errors['email'][0])

    def test_request_password_reset_form_when_email_had_wrong_symbols(self):
        email = "xФxx@m.ru"
        reset_form = UserRequestPasswordResetForm({'email': email})
        self.assertFalse(reset_form.is_valid())
        self.assertIn('Enter a valid email address.', reset_form.errors['email'][0])

    def test_request_password_reset_form_when_email_is_simple_string(self):
        email = "abc"
        reset_form = UserRequestPasswordResetForm({'email': email})
        self.assertFalse(reset_form.is_valid())
        self.assertEqual(reset_form.errors['email'][0], 'Enter a valid email address.')


class TestUserPasswordUpdateForm(TestCase):
    def setUp(self):
        random_name = str(uuid1())
        email = random_name + '@m.ru'
        self.user = User(username=random_name, email=email)
        self.user.set_password('12345678')
        self.user.firstname = 'user firstname'
        self.user.lastname = 'user lastname'
        self.user.patronymic = 'user patronymic'
        self.user.birth_date = timezone.datetime(year=1986, month=4, day=10)
        self.user.save()

    def test_user_password_update_form(self):
        newpass = 'qweasdzxc'
        update_form = UserPasswordUpdateForm({'password': newpass,
                                              'password_again': newpass},
                                             instance=self.user)
        self.assertTrue(update_form.is_valid())
        update_form.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(newpass))

    def test_user_password_update_form_when_passwords_are_differ(self):
        newpass = 'qweasdzxc'
        update_form = UserPasswordUpdateForm({'password': newpass,
                                              'password_again': newpass + "occasional symbols"},
                                             instance=self.user)
        self.assertFalse(update_form.is_valid())
        self.assertEqual(update_form.errors['__all__'][0], 'Passwords mismatch')

    def test_user_password_update_form_when_password_is_short(self):
        newpass = 'x' * 7
        update_form = UserPasswordUpdateForm({'password': newpass,
                                              'password_again': newpass},
                                             instance=self.user)
        self.assertFalse(update_form.is_valid())
        self.assertEqual(update_form.errors['__all__'][0], 'Password length must be at least 8 symbols')

    def test_user_password_update_form_when_password_is_too_large(self):
        newpass = 'x' * (MAX_PAGE_SIZE + 1)
        update_form = UserPasswordUpdateForm({'password': newpass,
                                              'password_again': newpass},
                                             instance=self.user)
        self.assertFalse(update_form.is_valid())
        self.assertEqual(update_form.errors['__all__'][0], 'You have only 640Kb for all purposes!')
