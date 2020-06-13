from django.urls import re_path, path
from Net640.apps.chat import views


app_name = 'chat'
urlpatterns = [
    # path for entering chat room with person
    re_path(r'^id(?P<user_id>([\d]*))/$', views.chat_room, name="chat_room"),
    # path for processing POST messages from user chat_room(basicaly sended by js as async request)
    path(r'action/', views.user_message_action, name="user_message_action"),
]
