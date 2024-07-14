from datetime import datetime,timezone,timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
import string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

def send_emails(email,subject,context,template_name,pdf_file=None,email_for="customer"):
        try:
            subject = subject
            message = render_to_string(template_name,context=context)
            text_content = strip_tags(message)
            from_email = settings.EMAIL_HOST_USER
            to_email = email
            # send_mail(subject, text_content, from_email, [to_email], fail_silently=False)
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(message, "text/html")

            if pdf_file:
                msg.attach(pdf_file.name, pdf_file.read(), 'application/pdf')

            msg.send()
        except Exception as e:
             print(e)
             raise RuntimeError("Error in sending email")
             return None