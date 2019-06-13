from datetime import datetime
from django.db import models
from django.conf import settings

from Net640.apps.images.models import user_directory_path
from Net640.mixin import LikesMixin


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
