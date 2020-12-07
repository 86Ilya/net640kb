import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from Net640.apps.images.ws_engine import ImageProcessing
from Net640.apps.user_profile.ws_engine import UserProfileWS
from Net640.apps.ws_eventbus.helpers import get_eventbus_room_name


logger = logging.getLogger('eventbus')


class EventBus(AsyncJsonWebsocketConsumer):
    """
    In APP_MATRIX app_name must be equal to the app name in vue js app.
    This name is used in communication on event bus
    for example 'image_actions.js':
        let app_name = 'image_processing';
        ...
        vue_images_processing.$eventBus.$on(app_name, (message) => { ...
    """
    APP_MATRIX = {"image_processing": ImageProcessing(),
                  "user_profile": UserProfileWS(),
                  }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            raise Exception("user is not authenticated")

        self.room_name = get_eventbus_room_name(self.scope['user'].id)
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
        # process messages from frontend here
        result = []
        for elem in content:
            logger.debug(f"EventBus.receive_json {elem}, {content}")
            app_name = elem['app_name']
            # TODO: await func call
            result.append({
                "app_name": app_name,
                "message": self.APP_MATRIX[app_name](self.scope['user'], elem['message'])
            })

        await self.send_json(result)

    async def eventbus(self, event):
        # messages from backend to frontend
        logger.debug(f"EventBus.eventbus {event}")
        body = event['body']
        await self.send_json([
            {
                # 'type': 'eventbus',
                'app_name': body['app_name'],
                'message': body['message']
            }]
        )
