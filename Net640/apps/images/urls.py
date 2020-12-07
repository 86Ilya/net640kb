from django.urls import path
from Net640.apps.images import views

app_name = 'images'
urlpatterns = [
    path(r'my_images/', views.user_images_view, name="my_images"),
]
