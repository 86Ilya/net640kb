from django.urls import path
from Net640.apps.user_posts import views

urlpatterns = [
        path(r'post_action/', views.user_post_action, name="user_post_action"),
        path(r'news/', views.user_news, name="user_news"),
]
