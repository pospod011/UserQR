from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(email, code):
    send_mail(
        subject='Подтверждение регистрации',
        message=f'Ваш код подтверждения: {code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
