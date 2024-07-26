from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from ...models import EmailAccount, EmailMessage, EmailAttachment

from email import message_from_string
from email.header import decode_header

from dateutil import parser

from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

import imaplib

import uuid


class Command(BaseCommand):
    help = 'Fetch emails from the email account'

    def handle(self, *args, **kwargs):
        # Получаем все учетные записи электронной почты из базы данных
        accounts = EmailAccount.objects.all()
        for account in accounts:
            self.stdout.write(f'Fetching emails for {account.email}')
            # Вызываем метод для получения писем для текущего аккаунта
            self.fetch_emails(account)

    def fetch_emails(self, account):
        # Подключаемся к почтовому серверу (imap.mail.ru в данном случае)
        mail = imaplib.IMAP4_SSL('imap.mail.ru')  # Настроить сервер в зависимости от провайдера
        mail.login(account.email, account.password)
        mail.select('inbox')

        # Получаем список всех писем в папке "Входящие"
        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()
        total_emails = len(email_ids)
        checked_emails = 0

        # Получаем слой канала для отправки обновлений через WebSocket
        channel_layer = get_channel_layer()

        for email_id in email_ids:
            checked_emails += 1
            # Отправляем обновление прогресса через WebSocket
            async_to_sync(channel_layer.group_send)(
                'email_progress',
                {
                    'type': 'update_progress',
                    'checked': checked_emails,
                    'total': total_emails
                }
            )

            # Получаем данные письма
            result, message_data = mail.fetch(email_id, '(RFC822)')
            raw_email = message_data[0][1].decode('utf-8')
            email_message = message_from_string(raw_email)

            # Декодируем тему письма
            subject, encoding = decode_header(email_message['subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')
            sent_date = parser.parse(email_message['date'])
            sent_date_str = sent_date.strftime('%Y-%m-%d %H:%M:%S')
            body = email_message.get_payload(decode=True)

            # Обрабатываем тело письма
            if isinstance(body, bytes):
                body = body.decode('utf-8', errors='ignore')
            elif isinstance(body, list):
                body = ''.join([part.get_payload(decode=True).decode('utf-8', errors='ignore') if isinstance(part.get_payload(decode=True), bytes) else part.get_payload(decode=True) for part in body])
            else:
                body = str(body)

            # Создаем объект EmailMessage и сохраняем его в базе данных
            email_obj = EmailMessage.objects.create(
                account=account,
                subject=subject,
                sent_date=sent_date,
                received_date=sent_date,  # Вы можете использовать другую дату здесь
                body=body,
            )

            attachments = []
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                file_data = part.get_payload(decode=True)
                filename = part.get_filename()
                content_type = part.get_content_type()
                size = len(file_data)

                if not filename:
                    filename = str(uuid.uuid4())  # Генерируем уникальное имя файла

                # Создаем объект EmailAttachment и сохраняем его в базе данных
                attachment = EmailAttachment(
                    message=email_obj,
                    filename=filename,
                    content_type=content_type,
                    size=size,
                )
                attachment.file.save(filename, ContentFile(file_data))
                attachment.save()
                attachments.append({
                    'filename': filename,
                    'content_type': content_type,
                    'size': size,
                })

            # Сохраняем вложения в объекте EmailMessage
            email_obj.attachments = attachments
            email_obj.save()

            # Отправляем обновление с информацией о новом письме через WebSocket
            async_to_sync(channel_layer.group_send)(
                'email_progress',
                {
                    'type': 'add_email',
                    'email': {
                        'id': email_obj.id,
                        'subject': email_obj.subject,
                        'sent_date': sent_date_str,
                        'received_date': sent_date_str,
                        'body': email_obj.body[:100],  # Ограничение длины тела для отображения
                        'attachments': attachments,
                    }
                }
            )

        # Выходим из почтового сервера
        mail.logout()
