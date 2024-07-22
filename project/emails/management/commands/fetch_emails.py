from django.core.management.base import BaseCommand
from ...models import EmailAccount, EmailMessage

from email import message_from_string

import imaplib


class Command(BaseCommand):
    help = 'Featch emails from the email account'

    def handle(self, *args, **kwargs):
        accounts = EmailAccount.objects.all()
        for account in accounts:
            self.stdout.write(f'Fetching emails for {account}')
            self.fetch_emails(account)

    def fetch_emails(self, account):
        mail = imaplib.IMAP4_SSL('imap.mail.ru')
        mail.login(account.email, account.password)
        mail.select('inbox')

        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()

        for email_id in email_ids:
            result, message_data = mail.fetch(email_id, '(RFC822)')
            raw_email = message_data[0][1].decode['utf-8']
            email_message = message_from_string(raw_email)

            subject = email_message['subject']
            send_date = email_message['date']
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            attachments = []

            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                attachment = {
                    'filename': part.get_filename(),
                    'content_type': part.get_content_type(),
                    'size': len(part.get_payload(decode=True))
                }
                attachments.append(attachment)

            EmailMessage.objects.create(
                account=account,
                subject=subject,
                send_date=send_date,
                received_date=send_date,
                body=body,
                attachments=attachments,
            )
        mail.logout()
