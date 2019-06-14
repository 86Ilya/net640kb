from django.urls import re_path, path
from Net640.apps.chat import views


urlpatterns = [
    # path for entering chat room with person
    re_path(r'^id(?P<person_id>([\d]*))/chat$', views.chat_room, name="chat_room"),
    # path for processing POST messages from user chat_room(basicaly sended by js as async request)
    path(r'message_action/', views.user_message_action, name="user_message_action"),
]
