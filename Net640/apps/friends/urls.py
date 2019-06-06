from django.urls import path, re_path
from Net640.apps.friends import views

urlpatterns = [
    path(r'friends/', views.friends_view, name="friends"),
    re_path(r'^id(?P<user_id>([\d]*))/$', views.user_view, name="user_view")
]
