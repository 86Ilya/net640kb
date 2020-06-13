from django.urls import path, re_path
from Net640.apps.friends import views

app_name = 'friends'
urlpatterns = [
    path(r'my_friends/', views.friends_view, name="my_friends"),
    re_path(r'^id(?P<user_id>([\d]*))/$', views.user_view, name="user_view")
]
