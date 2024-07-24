import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ProgressConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)("email_progress", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("email_progress", self.channel_name)

    def update_progress(self, event):
        checked = event['checked']
        total = event['total']
        self.send(text_data=json.dumps({
            'checked': checked,
            'total': total,
            'progress': int((checked / total) * 100)
        }))

    def add_email(self, event):
        email = event['email']
        self.send(text_data=json.dumps({
            'email': email
        }))
