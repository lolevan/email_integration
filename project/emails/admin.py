from django.contrib import admin

from .models import EmailAccount, EmailMessage, EmailAttachment

admin.site.register(EmailAccount)
admin.site.register(EmailMessage)
admin.site.register(EmailAttachment)
