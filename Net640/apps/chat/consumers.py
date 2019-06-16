import json
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer

from Net640.apps.chat.models import Message
from Net640.errors import NotEnoughSpace


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Class-consumer, which will accept WebSocket connections and
    process ws messages.
    """
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            raise Exception("user is not authenticated")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_{}'.format(self.room_name)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['message']
        response = None

        # Save message to database
        chat_message = Message(author=self.user, chat_room=self.room_name, content=content)
        try:
            chat_message.save()
            response = {
                'content': chat_message.content,
                'timestamp': chat_message.formatted_timestamp,
                'author': chat_message.author.username,
                'message_id': chat_message.id,
            }

        except NotEnoughSpace:
            # TODO send notificatin via update_flow
            return
        else:
            # Send message to room group
            await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': response})

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
        }))


class EventConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        self.room_name = str(self.scope['user'].id) + '_update_flow'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # TODO print -> logging
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
