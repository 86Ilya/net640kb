import json

from django.test import TestCase, Client
from django.urls import reverse

from Net640.apps.user_profile.models import User
from Net640.apps.user_posts.models import Post


class TestUserPosts(TestCase):
    def test_create_post(self):
        post_content = 'post by user1'
        user1 = User(username='test_create_post1', email='test_create_post1@m.ru')
        user1.save()

        post = Post(user=user1, content=post_content)
        post.save()

        post_from_db = Post.objects.get(user=user1)
        assert post_from_db.content == post_content
        assert post_from_db.user == user1

    def test_check_news_between_friends(self):
        post_content = 'post by user1'
        user1 = User(username='test_check_news_between_friends1',
                     email='test_check_news_between_friends1@m.ru')
        user1.save()
        post = Post(user=user1, content=post_content)
        post.save()

        user2 = User(username='test_check_news_between_friends2',
                     email='test_check_news_between_friends2@m.ru')
        user2.set_password('12345678')
        user2.save()

        user1.accept(user2)
        user2.accept(user1)

        client = Client()
        client.login(username='test_check_news_between_friends2', password='12345678')
        response = client.post(reverse('user_news'), {'action': 'get_news'})
        posts = json.loads(response.content)['posts']
        assert len(posts) == 1
        assert posts[0]['author'] == user1.username
        assert posts[0]['content'] == post_content

    def test_check_news_between_nonfriends(self):
        post_content = 'post by user1'
        user1 = User(username='test_check_news_between_nonfriends1',
                     email='test_check_news_between_nonfriends1@m.ru')
        user1.save()
        post = Post(user=user1, content=post_content)
        post.save()

        user2 = User(username='test_check_news_between_nonfriends2',
                     email='test_check_news_between_nonfriends2@m.ru')
        user2.set_password('12345678')
        user2.save()

        client = Client()
        client.login(username='test_check_news_between_nonfriends2', password='12345678')
        response = client.post(reverse('user_news'), {'action': 'get_news'})
        posts = json.loads(response.content)['posts']

        assert len(posts) == 0
        # check that post exists
        post_from_db = Post.objects.get(user=user1)
        assert post_from_db.content == post_content
        assert post_from_db.user == user1
