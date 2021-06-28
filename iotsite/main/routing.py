from django.urls import path

from .consumers import indexWSConsumer, clientWSConsumer

from django.conf.urls import url

ws_urlpatterns = [
	path('ws/index/', indexWSConsumer.as_asgi()),
	path('ws/<client_id>/', clientWSConsumer.as_asgi()),
]