from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from ..emails.routing import websocket_urlpatterns


# Создаем ASGI приложение для обработки различных типов подключений
application = ProtocolTypeRouter({
    # Обработка HTTP запросов с использованием стандартного ASGI приложения Django
    "http": get_asgi_application(),

    # Обработка WebSocket запросов с использованием middleware для аутентификации и маршрутизации
    "websocket": AuthMiddlewareStack(
        # Используем URLRouter для маршрутизации WebSocket запросов по определенным URL
        URLRouter(
            websocket_urlpatterns  # Маршруты для WebSocket из приложения emails
        )
    ),
})
