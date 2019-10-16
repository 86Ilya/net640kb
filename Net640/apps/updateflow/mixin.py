from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.core.cache import cache

from Net640.apps.updateflow.helpers import get_updateflow_room_name
CHANNEL_LAYER = get_channel_layer()


class UpdateFlowMixin:

    def msg_upd_page_size(self, size):
        room_name = get_updateflow_room_name(self.id)
        try:
            cache.incr(self.id, size)
        except ValueError:
            # it's an unlikely situation, so
            self.get_size()

        response = {'upd_user_page_size': size, 'error': False}
        async_to_sync(CHANNEL_LAYER.group_send)(room_name, {
            'type': 'update_flow',
            'message': response
        })
