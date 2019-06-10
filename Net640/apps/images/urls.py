from django.urls import path, re_path
from Net640.apps.images import views

urlpatterns = [
    path(r'my_images/', views.user_images_view, name="user_images"),
    path(r'image_action/', views.user_image_action, name="user_image_action"),
    re_path(r'^media/users/(?P<username>(\w*))/(?P<imagename>(.*))', views.get_image, name="get_image"),
    # re_path(r'^media/users/(?P<username>(\w*))/(?P<imagename>(.*))$', views.get_image, name="get_image_")
    # path(r'media/', views.get_image, name="get_image")
]
