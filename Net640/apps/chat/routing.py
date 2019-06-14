from django.urls import re_path

from Net640.apps.chat import consumers

chat_ws_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
]
