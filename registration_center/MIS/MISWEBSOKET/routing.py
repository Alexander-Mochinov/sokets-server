from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from trekking.trek.routing import websocket_urlpatterns as routing
from remote_connection.remote.routing import websocket_urlpatterns as remote
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing
        )
    ),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            remote
        )
    ),
})