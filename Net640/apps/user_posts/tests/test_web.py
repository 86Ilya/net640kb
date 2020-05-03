from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from django.test import override_settings
from django.urls import reverse

from Net640.testing.helpers import ChannelsBaseTestCase
from Net640.apps.user_posts.models import Post
from Net640.apps.user_profile.models import User


@override_settings(ALLOWED_HOSTS=['*'])  # Disable ALLOW_HOSTS
class TestPosts(ChannelsBaseTestCase):
    password = '12345678'

    def setUp(self):

        self.user1 = User(username='test_webinterface', email='user_testwebinterface@m.ru', is_active=True)
        self.user1.set_password(self.password)
        self.user1.save()

    def tearDown(self):
        # remove all posts
        Post.objects.all().delete()
        # remove user
        self.user1.delete()
        pass

    def test_post_creation(self):
        browser = self.selenium
        browser.get(self.live_server_url)
        browser.set_window_size(1920, 1000)
        browser.find_element(By.LINK_TEXT, "Log in").click()
        browser.find_element(By.NAME, "username").click()
        browser.find_element(By.NAME, "username").send_keys(self.user1.username)
        browser.find_element(By.NAME, "password").send_keys(self.password)
        browser.find_element(By.CSS_SELECTOR, ".btn").click()
        browser.find_element(By.ID, "id_content").click()
        browser.find_element(By.ID, "id_content").send_keys("test post")
        browser.find_element(By.CSS_SELECTOR, "[value='Send Post']").click()
        assert browser.find_element(By.CSS_SELECTOR, ".wordwrap").text.strip() == "test post"
        browser.get(self.live_server_url + reverse("user_profile:logout"))
        # delete our post from DB
        Post.objects.filter(content="test post").delete()
        User.objects.all()

    def test_post_like_creation(self):
        browser = self.selenium
        browser.get(self.live_server_url)
        browser.set_window_size(1920, 1000)
        browser.find_element(By.LINK_TEXT, "Log in").click()
        browser.find_element(By.NAME, "username").click()
        browser.find_element(By.NAME, "username").send_keys(self.user1.username)
        browser.find_element(By.NAME, "password").send_keys(self.password)
        browser.find_element(By.CSS_SELECTOR, ".btn").click()
        browser.find_element(By.ID, "id_content").click()
        browser.find_element(By.ID, "id_content").send_keys("test post")
        browser.find_element(By.CSS_SELECTOR, "[value='Send Post']").click()
        # click on the heart icon to add like
        browser.find_element(By.CSS_SELECTOR, ".fa-heart").click()
        assert browser.find_element(By.CSS_SELECTOR, ".badge").text == "1.0"
        browser.get(self.live_server_url + reverse("user_profile:logout"))

    def test_post_deletion(self):
        browser = self.selenium
        browser.get(self.live_server_url)
        browser.set_window_size(1920, 1000)
        browser.find_element(By.LINK_TEXT, "Log in").click()
        browser.find_element(By.NAME, "username").click()
        browser.find_element(By.NAME, "username").send_keys(self.user1.username)
        browser.find_element(By.NAME, "password").send_keys(self.password)
        browser.find_element(By.CSS_SELECTOR, ".btn").click()
        browser.find_element(By.ID, "id_content").click()
        browser.find_element(By.ID, "id_content").send_keys("test post")
        browser.find_element(By.CSS_SELECTOR, "[value='Send Post']").click()
        # click on the heart icon to add like
        assert browser.find_element(By.CSS_SELECTOR, ".wordwrap").text.strip() == "test post"
        # click on trash icon and remove post
        browser.find_element(By.CSS_SELECTOR, ".fa-trash-alt").click()
        # if there is a "test post" exists on the page that it's an error
        with self.assertRaises(NoSuchElementException):
            browser.find_element(By.CSS_SELECTOR, ".wordwrap")
        browser.get(self.live_server_url + reverse("user_profile:logout"))
