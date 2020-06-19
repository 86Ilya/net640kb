from django.test import TransactionTestCase
from Net640.apps.user_profile.models import User
from Net640.apps.user_posts.models import Post


class TestUserResourcesSize(TransactionTestCase):
    TRANSACTION_TEST_CASE = True

    def setUp(self):
        self.user = User(username='test_username', email='test_username@m.ru', password='12345678')
        self.user.save()

    def tearDown(self):
        Post.objects.all().delete()
        User.objects.all().delete()

    def test_base_size(self):
        # -[ RECORD 1 ]---+-------------------
        # id              | 3
        # password        | 12345678
        # last_login      |
        # is_superuser    | f
        # username        | test_username
        # email           | test_username@m.ru
        # firstname       |
        # lastname        |
        # patronymic      |
        # birth_date      |
        # is_active       | f
        # is_admin        | f
        # avatar          |
        # email_confirmed | f
        # is_staff        | f
        # avatar_size     | 0
        size_db = self.user._get_size()
        self.assertEqual(size_db, 46)

    def test_base_and_post_size(self):
        new_post = Post(user=self.user, content='test content', image='test image path', image_size=777)
        new_post.save()
        # -[ RECORD 1 ]-----------------------------
        # id         | 1
        # content    | test content
        # date       | 2020-06-18 12:06:07.451794+00
        # image      | test image path
        # user_id    | 1
        # image_size | 777

        size_db = self.user._get_size()
        self.assertEqual(size_db, 46 + 1 + 12 + 29 + 15 + 1 + 3 + 777)

    def test_base_and_post_and_postlike(self):
        new_post = Post(user=self.user, content='test content', image='test image path', image_size=777)
        new_post.save()
        new_post.likes.add(self.user)
        # -[ RECORD 1 ]
        # id      | 1
        # post_id | 1
        # user_id | 1

        size_db = self.user._get_size()
        self.assertEqual(size_db, 46 + 838 + 3)
