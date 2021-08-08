from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from validate_email import validate_email
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class RegistrationView(View):
    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):
        context = {
            'data': request.POST,
            'error_data': False
            }
        email = request.POST.get('email')
        username = request.POST.get('username')
        full_name = request.POST.get('name')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if len(password) < 8:
            messages.add_message(request, messages.ERROR, 'Password must contain at least 8 character')
            context['error_data'] = True

        if password != password2:
            messages.add_message(request, messages.ERROR, 'Password do not match')
            context['error_data'] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR, 'Email is not valid')
            context['error_data'] = True

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR, 'Email already used')
            context['error_data'] = True

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR, 'Username already used')
            context['error_data'] = True

        if context['error_data']:
            return render(request, 'auth/register.html', context)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.first_name = full_name
        user.last_name = full_name
        user.is_active = False
        user.save()

        current_site = get_current_site(request)
        email_subject = 'Active your Account'
        message = render_to_string('auth/activate.html',
        {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)

        }
        )

        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
        )

        email_message.send()

        messages.add_message(request, messages.SUCCESS, 'Your account has been created successfully')

        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        context = {
            'data': request.POST,
            'error_data': False
        }
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == '':
            messages.add_message(request, messages.ERROR, 'Username is required')
            context['error_data'] = True
        if password == '':
            messages.add_message(request, messages.ERROR, 'Password is required')
            context['error_data'] = True

        user = authenticate(request, username=username, password=password)

        if not user and not context['error_data']:
            messages.add_message(request, messages.ERROR, 'Invalid login or password')
            context['error_data'] = True

        if context['error_data']:
            return render(request, 'auth/login.html', status=401, context=context)

        login(request, user)
        return redirect('home')


class ActivateView(View):
    def get(self, request, uidb64, token):

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

        except Exception as identifier:
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.INFO, 'Your account has been activated successfully')
            return redirect('login')

        return render(request, 'auth/activate_error.html', status=401)


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Your has been logout successfully')
        return redirect('login')


class ResetPassword(View):
    def get(self, request):
        return render(request, 'auth/reset_password.html')

    def post(self, request):
        email = request.POST['email']

        if not User.objects.filter(email=email).exists():
            messages.add_message(request, messages.SUCCESS, 'Email is not valid')
            return render(request, 'auth/reset_password.html')

        user = User.objects.filter(email=email)

        if user.exists():
            current_site = get_current_site(request)
            email_subject = 'Reset Password'
            message = render_to_string('auth/confirm_reset_password.html',
                                       {
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                           'token': PasswordResetTokenGenerator().make_token(user[0])
                                       }
                                       )

            email_message = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
            )

            email_message.send()

        messages.add_message(request, messages.SUCCESS, 'Please, check yor email to reset password')

        return render(request, 'auth/reset_password.html')


class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        # import pdb
        # pdb.set_trace()
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.add_message(request, messages.INFO, 'Link was expired, enter your email to get a new one')
                return render(request, 'auth/reset_password.html')

        except DjangoUnicodeDecodeError as identifier:
            messages.add_message(request, messages.SUCCESS, 'Enter your new password')
            return render(request, 'auth/set_new_password.html', context)

        return render(request, 'auth/set_new_password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
            'error_data': False
        }

        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if len(password) < 8:
            messages.add_message(request, messages.ERROR, 'Password must contain at least 8 character')
            context['error_data'] = True

        if password != password2:
            messages.add_message(request, messages.ERROR, 'Password do not match')
            context['error_data'] = True

        if context['error_data'] == True:
            return render(request, 'auth/set_new_password.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Password Reset')

            return redirect('login')

        except DjangoUnicodeDecodeError as identifier:
            messages.add_message(request, messages.SUCCESS, 'Something went wrong')
            return render(request, 'auth/set_new_password.html', context)
