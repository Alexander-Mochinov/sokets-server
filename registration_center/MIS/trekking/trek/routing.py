from django.urls import path

from  trekking.trek import consumer
 
websocket_urlpatterns = [
    path('ws/coordinates/token=<user_token>/', consumer.TrakkingConsumer.as_asgi()),
]