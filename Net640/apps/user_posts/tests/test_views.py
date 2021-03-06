from uuid import uuid1

from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from Net640.apps.user_profile.models import User, RELATIONSHIP_FRIENDS, NO_RELATIONSHIP
from Net640.apps.user_posts.models import Post
from Net640.settings import MAX_PAGE_SIZE


class TestUserPostViews(TestCase):
    def setUp(self):
        random_name = str(uuid1())
        self.user = User(username=random_name, email=random_name + '@m.ru', is_active=True)
        self.user.set_password('12345678')
        self.user.save()

        random_name = str(uuid1())
        self.friend = User(username=random_name, email=random_name + '@m.ru', is_active=True)
        self.friend.set_password('12345678')
        self.friend.save()

    def test_create_post_from_mainpage(self):
        post_content = "test_create_post_from_mainpage"
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        post_from_db = Post.objects.get(user=self.user)
        self.assertEqual(post_from_db.content, post_content)

    def test_user_post_processing_action_get_posts(self):
        post_content = "test_user_post_processing_action_get_posts"
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        post_from_db = Post.objects.get(user=self.user)
        # get own posts from server
        post_from_action = client.post(reverse('posts:user_post_processing'), {'action': 'get_posts'}).json()['posts'][0]
        self.assertEqual(post_from_db.content, post_from_action['content'])

    def test_user_post_processing_like(self):
        post_content = "test_user_post_processing_like"
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        post_from_db = Post.objects.get(user=self.user)
        response = client.post(reverse('posts:user_post_processing'), {'action': 'like', 'id': post_from_db.id}).json()
        self.assertTrue(response['result'])
        self.assertEqual(post_from_db.get_rating(), response['likes'])

    def test_user_post_processing_dislike(self):
        post_content = "test_user_post_processing_dislike"
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        post_from_db = Post.objects.get(user=self.user)
        # set like
        response = client.post(reverse('posts:user_post_processing'), {'action': 'like', 'id': post_from_db.id}).json()
        self.assertTrue(response['result'])
        self.assertEqual(post_from_db.get_rating(), response['likes'])
        # remove like
        response = client.post(reverse('posts:user_post_processing'), {'action': 'dislike', 'id': post_from_db.id}).json()
        self.assertTrue(response['result'])
        self.assertEqual(post_from_db.get_rating(), response['likes'])

    def test_user_post_processing_remove(self):
        post_content = "test_user_post_processing_remove"
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        post_from_db = Post.objects.get(user=self.user)
        response = client.post(reverse('posts:user_post_processing'), {'action': 'remove', 'id': post_from_db.id}).json()
        self.assertTrue(response['result'])
        with self.assertRaises(ObjectDoesNotExist):
            Post.objects.get(user=self.user)

    def test_user_news_action_get_news(self):
        post_content = "test_user_news_action_get_news"
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        post_from_db = Post.objects.get(user=self.user)
        # must be friends
        self.friend.accept(self.user)
        self.user.accept(self.friend)
        self.assertEqual(self.user.check_relationship(self.friend), RELATIONSHIP_FRIENDS)
        # login as another user
        client.login(username=self.friend.username, password='12345678')
        # get news
        post_from_view = client.post(reverse('posts:news'), {'action': 'get_posts'}).json()['posts'][0]
        self.assertEqual(post_from_db.content, post_from_view['content'])
        self.assertEqual(post_from_db.id, post_from_view['id'])

    def test_create_post_from_mainpage_when_content_too_large(self):
        post_content = "1" * (MAX_PAGE_SIZE + 1)
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post_form'].errors['__all__'][0], 'Not enough space!')
        with self.assertRaises(ObjectDoesNotExist):
            Post.objects.get(user=self.user)

    def test_user_post_processing_remove_on_foreign_post(self):
        post_content = "test_user_post_processing_remove_on_foreign_post"
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        post_from_db = Post.objects.get(user=self.user)

        client.login(username=self.friend.username, password='12345678')
        response = client.post(reverse('posts:user_post_processing'), {'action': 'remove', 'id': post_from_db.id}).json()
        self.assertFalse(response['result'])
        self.assertEqual(Post.objects.get(user=self.user).content, post_from_db.content)

    def test_user_news_action_get_news_when_users_are_not_friends(self):
        post_content = "test_user_news_action_get_news_when_users_are_not_friends"
        client = Client()
        client.login(username=self.user.username, password='12345678')
        response = client.post(reverse('posts:mainpage'), {'content': post_content})
        self.assertEqual(response.status_code, 200)
        # check that users are not friends
        self.assertEqual(self.user.check_relationship(self.friend), NO_RELATIONSHIP)
        # login as another user
        client.login(username=self.friend.username, password='12345678')
        # get news
        post_from_view = client.post(reverse('posts:news'), {'action': 'get_posts'}).json()['posts']
        self.assertEqual(len(post_from_view), 0)
        # check that post exists
        post_from_db = Post.objects.get(user=self.user)
        self.assertEqual(post_from_db.content, post_content)
