import asyncio
import logging
from channels.layers import get_channel_layer

from django.db import models
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver

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
    likes = models.ManyToManyField(User, default=None, related_name="message_likes")

    def __unicode__(self):
        return '[{timestamp}] {author}: {content}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')

    def as_dict(self):
        return {'author': self.author.username, 'content': self.content, 'timestamp': self.formatted_timestamp}


@receiver(pre_save, sender=Message)
def recalculate_page_size_after_adding_message(sender, instance, raw, **kwargs):
    user = instance.author
    author_id = user.id
    # Calculate message size
    # use latest id as reference
    try:
        message_size = len(str(Message.objects.latest('id').id))
    except ObjectDoesNotExist:
        message_size = 1

    message_size += len(instance.content)
    message_size += len(str(instance.timestamp))
    message_size += len(str(instance.author_id))
    message_size += len(str(instance.chat_room))

    response = {'inc_user_page_size': message_size, 'error': False}

    if user.get_size() + message_size * 8 > MAX_PAGE_SIZE:
        response.update({'error': True, 'error_reason': 'not enough free space'})

    room_name = str(author_id) + '_update_flow'
    update_coro = CHANNEL_LAYER.group_send(room_name, {
        'type': 'update_flow',
        'message': response
    })
    event_loop = asyncio.get_event_loop()
    asyncio.ensure_future(update_coro, loop=event_loop)
    # raise error to prevent Message to save
    if response['error']:
        raise Exception(ERR_EXCEED_LIMIT)
