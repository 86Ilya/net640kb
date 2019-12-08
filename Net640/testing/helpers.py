import socket
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from channels.testing import ChannelsLiveServerTestCase


class ChannelsBaseTestCase(ChannelsLiveServerTestCase):
    # Bind to 0.0.0.0 to allow external access

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

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


def create_test_image(side_len=50):
    # TODO create big jpeg files
    file = BytesIO()
    image = Image.new('RGB', size=(side_len, side_len), color=(155, 0, 0))
    image.save(file, 'BMP')
    file.name = 'test.bmp'
    file.seek(0)
    content_type = 'image/bmp'
    return file, content_type
