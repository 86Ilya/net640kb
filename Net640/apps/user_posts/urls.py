from django.urls import path, re_path
from Net640.apps.user_posts import views

urlpatterns = [
    re_path(r'^post(?P<post_id>(\d*))/(?P<action>(dislike|like|remove))', views.user_post_action, name="user_post_action")
]
