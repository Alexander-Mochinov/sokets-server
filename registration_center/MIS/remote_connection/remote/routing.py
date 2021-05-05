from django.urls import path

from  remote_connection.remote import consumer
 
websocket_urlpatterns = [
    path('ws/remote/token=<user_token>/', consumer.RemoteConsumer.as_asgi()),
]