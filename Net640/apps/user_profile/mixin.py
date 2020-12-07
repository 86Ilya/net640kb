import logging
from django.core.cache import cache
from django.db import connection
from django.urls import reverse
from django.conf import settings

from Net640.apps.ws_eventbus.helpers import get_eventbus_room_name
from Net640.apps.ws_eventbus.sqs_connect import sqs_func_factory


class GetSizeMixin:
    """
    Class helper to calculate size of User data
    """

    def __cache(func):
        def wrapper(self, explicit=False):
            var = cache.get(self.id)
            if var is None or explicit:
                var = func(self)
                cache.set(self.id, var, settings.CACHE_TIMEOUT)
            return var
        return wrapper

    @__cache
    def get_size(self):
        return self._get_size()

    def _get_size(self):
        size = 0
        id = self.id
        cursor = connection.cursor()
        cursor.callproc('total_used_space', (id,))
        size = cursor.fetchone()[0]
        return size


send_message, _, delete_message = sqs_func_factory(settings.SQS_SYNC_ASYNC_EXCHANGE_QUEUE_URL, settings.SQS_RECV_PARAMS)
logger = logging.getLogger('default')


class SendMessagesToFrontEndMixin:
    """
    This class is responsible for sending the information
    to front-end 'base app'
    """
    ws_eventbus_type_name = 'eventbus'

    def __get_sqs_message_attributes(self):
        room_name = get_eventbus_room_name(self.id)
        attributes = {'room_name':
                      {'DataType': 'String',
                       'StringValue': room_name}}
        return attributes

    def __get_message_body(self, message):
        message_body = {'type': self.ws_eventbus_type_name,
                        'body': {'app_name': 'user_profile',
                                 'message': message
                                 }
                        }
        return message_body

    def msg_upd_page_size(self, size):
        try:
            cache.incr(self.id, size)
        except ValueError:
            # it's an unlikely situation, so
            self.get_size()

        message = {'action': 'upd_user_page_size',
                   'delta': size,
                   'result': True
                   }

        logger.debug(f"SendMessagesToFrontEndMixin.msg_upd_page_size user {self.id} {message}")

        send_message(MessageBody=self.__get_message_body(message),
                     MessageAttributes=self.__get_sqs_message_attributes())

    def msg_recalculate_page_size(self):
        size = self._get_size()
        cache.set(self.id, size, settings.CACHE_TIMEOUT)

        message = {'user_page_size': size, 'error': False}
        send_message(MessageBody=self.__get_message_body(message),
                     MessageAttributes=self.__get_sqs_message_attributes())

    def send_info_about_new_request_to_friends(self, person):

        message = {'upd_relationship_waiting_for_accept': {'person': person.username,
                                                           'ignore_page': reverse('friends:my_friends')},
                   'error': False}

        send_message(MessageBody=self.__get_message_body(message),
                     MessageAttributes=self.__get_sqs_message_attributes())
