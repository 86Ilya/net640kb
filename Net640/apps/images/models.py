import uuid
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import models
from django.conf import settings

from Net640.mixin import LikesMixin


CHANNEL_LAYER = get_channel_layer()


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    return 'users/{0}/{1}.{2}'.format(instance.user.username, uuid.uuid4(), ext)


def user_avatar_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/<username>/images/<filename>
    return 'users/{0}/avatar/avatar.{1}'.format(instance.username, filename.split('.')[-1])


class Image(LikesMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, default=None, related_name="message_likes")

    def delete(self, *args, **kwargs):
        author_id = str(self.user.id)
        image_size = len(str(self.id))
        image_size += len(self.description)
        image_size += self.image.size
        image_size += len(str(self.uploaded_at))
        image_size += len(author_id)

        super().delete(*args, **kwargs)
        if image_size:
            # send decrement info
            response = {'dec_user_page_size': image_size, 'error': False}
            room_name = str(author_id) + '_update_flow'
            # TODO make it async?
            async_to_sync(CHANNEL_LAYER.group_send)(room_name, {
                'type': 'update_flow',
                'message': response
            })
