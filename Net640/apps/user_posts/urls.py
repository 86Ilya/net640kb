from django.urls import path, re_path
from Net640.apps.user_posts import views

app_name = 'posts'
urlpatterns = [
    path(r'', views.mainpage_view, name="mainpage"),
    # TODO move to rest api
    re_path(r'post/(?P<user_id>[\d]*)?', views.user_post_processing, name="user_post_processing"),
    re_path(r'comment/(?P<post_id>[\d]*)?', views.user_comment_processing, name="user_comment_processing"),
    path(r'news/', views.user_news, name="news"),
]
