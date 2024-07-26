from django.db import models


class EmailAccount(models.Model):
    '''
    Модель для хранения учетных данных почтовых аккаунтов
    '''
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)


class EmailMessage(models.Model):
    '''
    Модель для хранения информации о сообщениях электронной почты
    '''
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField()
    body = models.TextField()
    attachments = models.JSONField(default=list)

    def __str__(self):
        return self.subject


class EmailAttachment(models.Model):
    '''
    Модель для хранения информации о вложениях сообщений электронной почты
    '''
    message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name='email_attachments')
    file = models.FileField(upload_to='attachments/')
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size = models.IntegerField()

    def __str__(self):
        return self.filename
