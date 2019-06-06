import json
from channels.generic.websocket import AsyncWebsocketConsumer, JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync

from Net640.apps.chat.models import Message
from Net640.errors import NotEnoughSpace


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            raise Exception("user is not authenticated")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # print(self.room_group_name)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # breakpoint()
        # print(self.scope['user'], " joined to grp: ", self.room_group_name)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        # TODO is chek user in self.connect is enough to keep security?
        # Or I need to check user on every receive event?
        text_data_json = json.loads(text_data)
        content = text_data_json['message']
        response = None

        # Save message to database
        chat_message = Message(author=self.user, chat_room=self.room_name, content=content)
        try:
            # breakpoint()
            chat_message.save()
            response = {
                        'content': chat_message.content,
                        'timestamp': chat_message.formatted_timestamp,
                        'author': chat_message.author.username,
                       }

        # TODO how to do this right? Too much errors in log
        except NotEnoughSpace:
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
        # print("Closed websocket with code: ", close_code)
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        # self.close()

    async def receive_json(self, content, **kwargs):
        # print("Received event: {}".format(content))
        await self.send_json(content)

    # ------------------------------------------------------------------------------------------------------------------
    # Handler definitions! handlers will accept their corresponding message types. A message with type event.alarm
    # has to have a function event_alarm
    # ------------------------------------------------------------------------------------------------------------------

    async def update_flow(self, event):
        await self.send_json(
            {
                'type': 'update_flow',
                'message': event['message']
            }
        )
