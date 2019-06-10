from datetime import datetime
from django.db import models

from Net640.apps.user_profile.models import User
from Net640.mixin import LikesMixin


class Post(LikesMixin, models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(default=datetime.now, blank=True)
    likes = models.ManyToManyField(User, default=None, related_name="post_likes")

    class Meta:
        ordering = ["-date"]
