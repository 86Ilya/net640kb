from django.urls import re_path, path
from Net640.apps.chat import views


urlpatterns = [
    # path(r'^$', views.index, name='index'),
    re_path(r'^id(?P<person_id>([\d]*))/chat$', views.chat_room, name="chat_room"),
    path(r'message_action/', views.user_message_action, name="user_message_action"),
    # re_path(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),
]
