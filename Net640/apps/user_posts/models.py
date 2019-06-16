from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db import models
from django.conf import settings
from django.urls import reverse

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

    def as_dict(self, executor):
        return {'content': self.content,
                'user_has_like': self.has_like(executor),
                'is_owner': self.user == executor,
                'rating': round(self.get_rating(), 1),
                'author': self.user.username,
                'author_page': reverse('user_view', kwargs={'user_id': self.user.id}),
                'date': self.date.strftime('%b %d, %Y'),
                'image_url': self.get_image_url(),
                'id': self.id,
                'author_thumbnail_url': self.user.get_thumbnail_url(), }
