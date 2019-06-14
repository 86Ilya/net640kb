from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from Net640.apps.chat.routing import chat_ws_urlpatterns
from Net640.apps.updateflow.routing import updateflow_ws_urlpatterns

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat_ws_urlpatterns + updateflow_ws_urlpatterns
        )
    ),
})
