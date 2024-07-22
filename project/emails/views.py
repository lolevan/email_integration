from django.shortcuts import render

from .models import EmailMessage


def email_list(request):
    messages = EmailMessage.objects.all()
    return render(request, 'emails/email_list.html', {'messages': messages})



