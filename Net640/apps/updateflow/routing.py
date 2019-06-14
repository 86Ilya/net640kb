from django.urls import re_path

from Net640.apps.updateflow import consumers

updateflow_ws_urlpatterns = [
    re_path(r'^ws/update_flow/$', consumers.EventConsumer),
]
