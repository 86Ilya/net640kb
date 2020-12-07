from django.urls import re_path

from Net640.apps.ws_eventbus import consumers

ws_eventbus_urlpatterns = [
    re_path(r'^ws/event_bus/$', consumers.EventBus),
]
