from django.core.management.base import BaseCommand
from ...models import EmailAccount, EmailMessage
from email import message_from_string
from email.header import decode_header
import imaplib
from dateutil import parser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Command(BaseCommand):
    help = 'Fetch emails from the email account'

    def handle(self, *args, **kwargs):
        accounts = EmailAccount.objects.all()
        for account in accounts:
            self.stdout.write(f'Fetching emails for {account.email}')
            self.fetch_emails(account)

    def fetch_emails(self, account):
        mail = imaplib.IMAP4_SSL('imap.mail.ru')  # Adjust the server based on the provider
        mail.login(account.email, account.password)
        mail.select('inbox')

        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()
        total_emails = len(email_ids)
        checked_emails = 0

        channel_layer = get_channel_layer()

        for email_id in email_ids:
            checked_emails += 1
            async_to_sync(channel_layer.group_send)(
                'email_progress',
                {
                    'type': 'update_progress',
                    'checked': checked_emails,
                    'total': total_emails
                }
            )

            result, message_data = mail.fetch(email_id, '(RFC822)')
            raw_email = message_data[0][1].decode('utf-8')
            email_message = message_from_string(raw_email)

            subject, encoding = decode_header(email_message['subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')
            sent_date = parser.parse(email_message['date'])
            sent_date_str = sent_date.strftime('%Y-%m-%d %H:%M:%S')
            body = email_message.get_payload(decode=True)

            if isinstance(body, bytes):
                body = body.decode('utf-8', errors='ignore')
            elif isinstance(body, list):
                body = ''.join([part.get_payload(decode=True).decode('utf-8', errors='ignore') if isinstance(part.get_payload(decode=True), bytes) else part.get_payload(decode=True) for part in body])
            else:
                body = str(body)

            attachments = []

            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                attachment = {
                    'filename': part.get_filename(),
                    'content_type': part.get_content_type(),
                    'size': len(part.get_payload(decode=True)),
                }
                attachments.append(attachment)

            email_obj = EmailMessage.objects.create(
                account=account,
                subject=subject,
                sent_date=sent_date,
                received_date=sent_date,  # You might want to use another date here
                body=body,
                attachments=attachments,
            )

            async_to_sync(channel_layer.group_send)(
                'email_progress',
                {
                    'type': 'add_email',
                    'email': {
                        'id': email_obj.id,
                        'subject': email_obj.subject,
                        'sent_date': sent_date_str,
                        'received_date': sent_date_str,
                        'body': email_obj.body[:100],  # Limit body length for display
                        'attachments': email_obj.attachments,
                    }
                }
            )

        mail.logout()
