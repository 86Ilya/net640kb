import uuid

from django.db import models
from django.conf import settings

from Net640.mixin import LikesMixin


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/<username>/<uuid4>.<ext>
    ext = filename.split('.')[-1]
    return 'users/{0}/{1}.{2}'.format(instance.user.username, uuid.uuid4(), ext)


def user_avatar_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/<username>/avatar/avatar.<ext>
    return 'users/{0}/avatar/avatar.{1}'.format(instance.username, filename.split('.')[-1])


class Image(LikesMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to=user_directory_path)
    image_size = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, default=None, related_name="message_likes")

    class Meta:
        app_label = 'images'

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
            self.user.msg_upd_page_size(-image_size)
