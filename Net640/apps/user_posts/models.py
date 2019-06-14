from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db import models
from django.conf import settings

from Net640.apps.images.models import user_directory_path
from Net640.mixin import LikesMixin
from Net640.apps.updateflow.helpers import get_updateflow_room_name


CHANNEL_LAYER = get_channel_layer()


class Post(LikesMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(default=datetime.now, blank=True)
    image = models.ImageField(upload_to=user_directory_path)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, default=None, related_name="post_likes")

    class Meta:
        ordering = ["-date"]

    def get_image_url(self):
        if self.image:
            return self.image.url

    def delete(self, *args, **kwargs):
        post_size = 0
        try:
            post_size += len(str(self.id))
            post_size += len(str(self.user.id))
            post_size += len(self.content)
            post_size += len(str(self.user_id))
            post_size += len(str(self.date))
            if self.image:
                post_size += len(str(self.image))
            # TODO calculate likes
            if post_size:
                # send decrement info
                response = {'dec_user_page_size': post_size, 'error': False}
                room_name = get_updateflow_room_name(self.user_id)
                async_to_sync(CHANNEL_LAYER.group_send)(room_name, {
                    'type': 'update_flow',
                    'message': response
                })
        finally:
            super().delete(*args, **kwargs)
