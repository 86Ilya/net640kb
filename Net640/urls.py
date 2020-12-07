from django.urls import path, include, re_path
from Net640.settings import MEDIA_ROOT, MEDIA_URL, STATIC_URL, STATIC_ROOT
from django.conf.urls.static import static

import Net640.apps.images.views as image_views

try:
    from Net640.local_settings import DEBUG
except ImportError:
    from Net640.settings import DEBUG

media_url = [
    # next function is working in cooperation with nginx:
    #  - nginx recieve request for some resource in /media/*
    #  - ngnix moves this request to views.get_image
    #  - get_image checks permissions and return resource or return 404
    re_path(r'^media/users/(?P<username>(\w*))/(?P<imagename>(.*))', image_views.get_image, name="get_image"),
]


urlpatterns = [
    path('', include('Net640.apps.user_posts.urls', namespace='posts')),
    path('user/', include('Net640.apps.user_profile.urls', namespace='profile')),
    path('friends/', include('Net640.apps.friends.urls', namespace='friends')),
    path('chat/', include('Net640.apps.chat.urls', namespace='chat')),
    path('images/', include('Net640.apps.images.urls', namespace='images')),
] + media_url

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
