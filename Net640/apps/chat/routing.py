from django.urls import re_path

from Net640.apps.chat import consumers

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
    re_path(r'^ws/update_flow/$', consumers.EventConsumer),
]
