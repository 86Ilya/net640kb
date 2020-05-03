from django.contrib import admin
from django.urls import path, include
from Net640.settings import MEDIA_ROOT, MEDIA_URL, STATIC_URL, STATIC_ROOT
from django.conf.urls.static import static

try:
    from Net640.local_settings import DEBUG
except ImportError:
    from Net640.settings import DEBUG


urlpatterns = [
    path('user/', include('Net640.apps.user_profile.urls', namespace='user_profile')),
    path('', include('Net640.apps.friends.urls')),
    path('', include('Net640.apps.chat.urls')),
    path('', include('Net640.apps.images.urls')),
    path('', include('Net640.apps.user_posts.urls')),
    path('admin/', admin.site.urls),
]
if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
