from uuid import uuid1
from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from Net640.apps.user_posts.forms import PostForm
from Net640.apps.user_profile.models import User


def create_test_image(side_len=50):
    # TODO create big jpeg files
    file = BytesIO()
    image = Image.new('RGB', size=(side_len, side_len), color=(155, 0, 0))
    image.save(file, 'BMP')
    file.name = 'test.bmp'
    file.seek(0)
    content_type = 'image/bmp'
    return file, content_type


class TestUserPostForm(TestCase):

    def setUp(self):
        random_name = str(uuid1())
        self.user = User(username=random_name, email=random_name + '@m.ru')
        self.user.save()

    def test_create_correct_post_by_form(self):
        user_post_form_data = {'content': 'test content'}
        user_post_form = PostForm(user_post_form_data, user=self.user)
        self.assertTrue(user_post_form.is_valid())

    def test_create_correct_post_by_form_with_image(self):
        img_file, content_type = create_test_image()
        img_dict = {'image': SimpleUploadedFile('myimage.bmp', img_file.read(), content_type)}
        user_post_form_data = {'content': 'test content'}
        user_post_form = PostForm(user_post_form_data, img_dict, user=self.user)
        self.assertTrue(user_post_form.is_valid())

    def test_create_incorrect_anonymous_post_by_form(self):
        user_post_form_data = {'content': 'test content'}
        user_post_form = PostForm(user_post_form_data)
        self.assertFalse(user_post_form.is_valid())
        self.assertEqual(user_post_form.errors['__all__'][0], 'Anonymous posts are not allowed')

    def test_create_incorrect_oversized_post_by_form(self):
        img_file, content_type = create_test_image(1000)
        img_dict = {'image': SimpleUploadedFile('myimage.bmp', img_file.read(), content_type)}
        user_post_form_data = {'content': 'test content'}
        user_post_form = PostForm(user_post_form_data, img_dict, user=self.user)
        self.assertFalse(user_post_form.is_valid())
        self.assertEqual(user_post_form.errors['__all__'][0], 'Not enough space!')
