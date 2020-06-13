from django.urls import path, re_path
from Net640.apps.images import views

app_name = 'images'
urlpatterns = [
    path(r'my_images/', views.user_images_view, name="my_images"),
    # TODO move to rest api
    path(r'action/', views.user_image_action, name="user_image_action"),
]
