from channels.generic.websocket import AsyncJsonWebsocketConsumer
from Net640.apps.updateflow.helpers import get_updateflow_room_name


class EventConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            raise Exception("user is not authenticated")

        self.room_name = get_updateflow_room_name(self.scope['user'].id)
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        await self.send_json(content)

    async def update_flow(self, event):
        await self.send_json(
            {
                'type': 'update_flow',
                'message': event['message']
            }
        )
