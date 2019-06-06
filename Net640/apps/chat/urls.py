from django.urls import re_path
from Net640.apps.chat import views


urlpatterns = [
    # path(r'^$', views.index, name='index'),
    re_path(r'^id(?P<person_id>([\d]*))/chat$', views.chat_room, name="chat_room")
    # re_path(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),
]
