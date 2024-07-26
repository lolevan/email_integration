import json

from channels.generic.websocket import WebsocketConsumer

from asgiref.sync import async_to_sync


class ProgressConsumer(WebsocketConsumer):
    def connect(self):
        # При подключении WebSocket клиента, принимаем соединение
        self.accept()
        # Добавляем канал в группу "email_progress"
        async_to_sync(self.channel_layer.group_add)("email_progress", self.channel_name)

    def disconnect(self, close_code):
        # При отключении WebSocket клиента, удаляем канал из группы "email_progress"
        async_to_sync(self.channel_layer.group_discard)("email_progress", self.channel_name)

    def update_progress(self, event):
        # Обрабатываем событие обновления прогресса
        checked = event['checked']
        total = event['total']
        # Отправляем обновленный прогресс на клиент
        self.send(text_data=json.dumps({
            'checked': checked,
            'total': total,
            'progress': int((checked / total) * 100)  # Вычисляем процент выполнения
        }))

    def add_email(self, event):
        # Обрабатываем событие добавления нового письма
        email = event['email']
        # Отправляем информацию о новом письме на клиент
        self.send(text_data=json.dumps({
            'email': email
        }))
