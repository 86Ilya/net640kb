import os
import logging

from django.db import models
from django.conf import settings
from django.utils import timezone

from Net640.apps.images.models import user_directory_path
from Net640.mixin import LikesMixin
from Net640.apps.user_posts.mixin import AsDictMessageMixin
from Net640.apps.user_posts.exceptions import PostException


class Post(LikesMixin, AsDictMessageMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now, blank=True)
    image = models.ImageField(upload_to=user_directory_path)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, default=None, related_name="post_likes")

    class Meta:
        ordering = ["-date"]
        app_label = 'user_posts'

    def get_image_url(self):
        if self.image:
            return self.image.url

    def get_size(self):
        """ calculate post size """
        # TODO Currently, this method calculates the size approximately. Need to calculate likes.
        try:
            post_size = 0
            post_size += len(str(self.id))
            post_size += len(str(self.user.id))
            post_size += len(self.content)
            post_size += len(str(self.user_id))
            post_size += len(str(self.date))
            if self.image:
                post_size += self.image.size
        except Exception as error:
            raise PostException("Got error when calculating post size {}".format(error))
        return post_size

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            post_size = self.get_size()
            if post_size:
                # send increment info
                self.user.msg_upd_page_size(post_size)
        except PostException as error:
            logging.error(error)

    def delete(self, *args, **kwargs):
        try:
            post_size = self.get_size()
            if post_size:
                # send decrement info
                self.user.msg_upd_page_size(-post_size)
        except PostException as error:
            logging.error(error)
        finally:
            super().delete(*args, **kwargs)
            if self.image:
                os.remove(self.image.path)

    def as_dict(self, executor):
        result = super().as_dict(executor)
        result.update({'comments': [comment.as_dict(executor) for comment in Comment.objects.filter(post=self)],
                       'image_url': self.get_image_url()})
        return result


class Comment(LikesMixin, AsDictMessageMixin, models.Model):
    """
    Comment model for user post
    """
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, default=None, related_name="comment_likes")

    class Meta:
        ordering = ['-date']
        app_label = 'user_posts'
