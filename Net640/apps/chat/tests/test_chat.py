import socket

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.test import override_settings
from channels.testing import ChannelsLiveServerTestCase

from Net640.apps.user_profile.models import User


@override_settings(ALLOWED_HOSTS=['*'])  # Disable ALLOW_HOSTS
class TestTestchat(ChannelsLiveServerTestCase):
    # Bind to 0.0.0.0 to allow external access
    host = '0.0.0.0'
    server_static = True
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set host to externally accessible web server address
        cls.host = socket.gethostbyname(socket.gethostname())

        # Instantiate the remote WebDriver
        # 'selenium' is docker container configured in docker-compose-develop.yml
        cls.selenium = webdriver.Remote(command_executor='http://selenium:4444/wd/hub',
                                        desired_capabilities=DesiredCapabilities.FIREFOX)
        cls.selenium.implicitly_wait(7)

        # create two users
        cls.password = '12345678'

        cls.user1 = User(username='test_ui_1', email='user1@m.ru', is_active=True)
        cls.user1.set_password(cls.password)
        cls.user1.save()

        cls.user2 = User(username='test_ui_2', email='user2@m.ru', is_active=True)
        cls.user2.set_password(cls.password)
        cls.user2.save()

        # create relationships between them
        cls.user1.accept(cls.user2)
        cls.user2.accept(cls.user1)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def user1_send_chatmessage_to_user2(self):
        browser = self.selenium
        browser.get(self.live_server_url)
        browser.set_window_size(1920, 1000)
        element = browser.find_element(By.LINK_TEXT, "Log in")
        actions = ActionChains(browser)
        actions.move_to_element(element).perform()
        # pdb.set_trace()
        browser.find_element(By.LINK_TEXT, "Log in").click()
        browser.find_element(By.NAME, "username").click()
        browser.find_element(By.NAME, "username").send_keys(self.user1.username)
        browser.find_element(By.NAME, "password").send_keys(self.password)
        browser.find_element(By.CSS_SELECTOR, ".btn").click()
        browser.find_element(By.ID, "friends_main_menu_button").click()
        browser.find_element(By.LINK_TEXT, "test_ui_2 ()").click()
        browser.find_element(By.LINK_TEXT, "Chat").click()
        browser.find_element(By.ID, "send_message_form_text").click()
        browser.find_element(By.ID, "send_message_form_text").send_keys("Hi! This is test message for user id2")
        browser.find_element(By.ID, "send_message_btn").click()
        mymessage = browser.find_element(By.CLASS_NAME, "chat__table_message_written_by_owner")
        assert mymessage.text == "Hi! This is test message for user id2"
        browser.get(self.live_server_url + "/logout/")

    def user2_check_chatmessage_from_user1(self):
        browser = self.selenium
        browser.get(self.live_server_url)
        browser.set_window_size(1920, 1020)
        element = browser.find_element(By.LINK_TEXT, "Log in")
        actions = ActionChains(browser)
        actions.move_to_element(element).perform()
        browser.find_element(By.LINK_TEXT, "Log in").click()
        browser.find_element(By.NAME, "username").click()
        browser.find_element(By.NAME, "username").send_keys(self.user2.username)
        browser.find_element(By.NAME, "password").send_keys(self.password)
        browser.find_element(By.CSS_SELECTOR, ".btn").click()
        browser.find_element(By.ID, "friends_main_menu_button").click()
        browser.find_element(By.LINK_TEXT, "test_ui_1 ()").click()
        browser.find_element(By.LINK_TEXT, "Chat").click()
        browser.find_element(By.ID, "send_message_form_text").click()
        browser.find_element(By.ID, "send_message_form_text").send_keys("Hi! This is test message for user id1")
        browser.find_element(By.ID, "send_message_btn").click()
        # check message from user1
        all_messages = browser.find_elements(By.CLASS_NAME, "chat__table_message_content")
        user1message = list(filter(lambda m: "chat__table_message_written_by_owner" not in m.get_attribute("class"),
                                   all_messages))[0]

        assert user1message.text == "Hi! This is test message for user id2"
        # check own message
        mymessage = browser.find_element(By.CLASS_NAME, "chat__table_message_written_by_owner")
        assert mymessage.text == "Hi! This is test message for user id1"
        browser.get(self.live_server_url + "/logout/")

    def test_chat_messaging(self):
        self.user1_send_chatmessage_to_user2()
        self.user2_check_chatmessage_from_user1()
