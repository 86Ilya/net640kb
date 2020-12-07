from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings


from Net640.apps.chat.routing import chat_ws_urlpatterns
from Net640.apps.ws_eventbus.routing import ws_eventbus_urlpatterns
# FIXME: wrong place for this
from Net640.apps.ws_eventbus.SQSProcessing import SQSProcessing

sqs_worker = SQSProcessing(settings.SQS_SYNC_ASYNC_EXCHANGE_QUEUE_URL, settings.SQS_RECV_PARAMS)
sqs_worker.start()

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat_ws_urlpatterns + ws_eventbus_urlpatterns
        )
    ),
})
