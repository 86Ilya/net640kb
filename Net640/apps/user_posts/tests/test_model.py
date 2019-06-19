from uuid import uuid1

from django.test import TestCase

from Net640.apps.user_profile.models import User
from Net640.apps.user_posts.models import Post


class TestUserPosts(TestCase):
    def setUp(self):
        random_name = str(uuid1())
        self.user = User(username=random_name, email=random_name + '@m.ru')
        self.user.set_password('12345678')
        self.user.save()

    def test_create_post(self):
        post_content = 'test_create_post'
        post = Post(user=self.user, content=post_content)
        post.save()

        post_from_db = Post.objects.get(user=self.user)
        self.assertEqual(post_from_db.content, post_content)
        self.assertEqual(post_from_db.user, self.user)
