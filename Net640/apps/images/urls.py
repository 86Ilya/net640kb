from django.urls import path, re_path
from Net640.apps.images import views

urlpatterns = [
    path(r'my_images/', views.user_images_view, name="user_images"),
    re_path(r'^id(?P<user_id>([\d]*))/images/(?P<image_name>([\-\.\w_0-9]*))$', views.get_image, name="get_image")
]
