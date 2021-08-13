from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View, generic
from django.views.generic import CreateView, TemplateView
from account.forms import *

User = get_user_model()


class RegistrationView(SuccessMessageMixin, CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('home')
    success_message = "Your registration was successful. An activation link has been sent to you email. Please, check."


# http://127.0.0.1:8000/account/activate/?u=24weaf25
class ActivationView(View):
    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save()
            return render(request, 'auth/register_activate.html', {})

        except Exception as identifier:
            user = None
        return render(request, 'auth/register_error.html', status=401)


class LoginView(View):
    def get(self, request):
        print(request)
        return render(request, 'auth/login.html')

    def post(self, request):
        print(request)
        context = {
            'data': request.POST,
            'error_data': False
        }
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == '':
            messages.add_message(request, messages.ERROR, 'Email is required')
            context['error_data'] = True
        if password == '':
            messages.add_message(request, messages.ERROR, 'Password is required')
            context['error_data'] = True

        user = authenticate(request, username=username, password=password)
        print(user)

        if not user and not context['error_data']:
            messages.add_message(request, messages.ERROR, 'Invalid email or password')
            context['error_data'] = True

        if context['error_data']:
            return render(request, 'auth/login.html', status=401, context=context)

        login(request, user)
        return redirect('home')


class ChangePasswordView(View):
    def post(self, request):
        form = ChangePasswordForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('auth/login'))
        return render(request, 'auth/change_password.html', {'form': form})

    def get(self, request):
        form = ChangePasswordForm(request=request)
        return render(request, 'auth/change_password.html', {'form': form})


class ForgotPasswordView(View):
    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            form.send_new_password()
            messages.add_message(request, messages.SUCCESS, 'We sent a new password to your email, please check')
            return redirect(reverse_lazy('login'))
        return render(request, 'auth/reset_password.html', {'form': form})

    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, 'auth/reset_password.html', {'form': form})


# class UserProfileView(generic.DetailView):
#     model = User
#     template_name = 'auth/profile.html'

def profile(request):
    return render(request, 'auth/profile.html')
