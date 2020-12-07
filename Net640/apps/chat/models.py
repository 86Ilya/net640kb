from channels.layers import get_channel_layer

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from Net640.apps.user_profile.models import User
from Net640.errors import ERR_EXCEED_LIMIT
from Net640.settings import MAX_PAGE_SIZE


CHANNEL_LAYER = get_channel_layer()


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, related_name='message_author', on_delete=models.CASCADE)
    chat_room = models.TextField()
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        app_label = 'chat'

    def save(self, *args, **kwargs):
        # Calculate message size
        # use latest id as reference
        try:
            message_size = len(str(Message.objects.latest('id').id))
        except ObjectDoesNotExist:
            message_size = 1
        message_size += len(self.content)
        message_size += len(str(self.author_id))
        message_size += len(str(self.timestamp))
        message_size += len(str(self.author_id))
        message_size += len(str(self.chat_room))

        if self.author.get_size() + message_size * 8 > MAX_PAGE_SIZE:
            raise Exception(ERR_EXCEED_LIMIT)
        self.author.msg_upd_page_size(message_size)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        message_size = 0
        try:
            message_size += len(str(self.id))
            message_size += len(self.content)
            message_size += len(str(self.author_id))
            message_size += len(str(self.timestamp))
            message_size += len(str(self.author_id))
            message_size += len(str(self.chat_room))
            if message_size:
                # send decrement info
                self.author.msg_upd_page_size(-message_size)
        finally:
            super().delete(*args, **kwargs)

    def __str__(self):
        return '[{timestamp}] {author}: {content}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')

    def as_dict(self):
        return {'author': self.author.username, 'content': self.content, 'timestamp': self.formatted_timestamp}
