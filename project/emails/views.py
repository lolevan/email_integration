import threading

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command

from .models import EmailMessage


@csrf_exempt
def fetch_emails(request):
    def fetch():
        call_command('fetch_emails')

    thread = threading.Thread(target=fetch)
    thread.start()
    return JsonResponse({'status': 'Fetching emails started'})


def email_list(request):
    messages = EmailMessage.objects.all()
    return render(request, 'emails/email_list.html', {'messages': messages})
