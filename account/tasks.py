from django.core.mail import send_mail
from survey.celery_ import app


@app.task
def send_activation_mail(email, activation_code):
    message = f'http://127.0.0.1:8000/account/register_activate/{activation_code}'
    send_mail('Активация аккаунта', message, 'test@gmail.com', [email])


