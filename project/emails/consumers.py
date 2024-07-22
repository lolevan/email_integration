from channels.generic.websocket import WebsocketConsumer

import json


class ProgressConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def receive(self, text_data):
        data = json.loads(text_data)
        progress = data['progress']
        self.send(text_data=json.dumps({
            'progress': progress
        }))
