from django import forms
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from account.tasks import send_activation_mail

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(min_length=8, widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(min_length=8, widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'full_name', 'image']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('The user is already registered')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already exists, please choose another one')
        return username

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.pop('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError('Password mismatch')
        return self.cleaned_data

    def save(self):
        user = User.objects.create(**self.cleaned_data)
        user.create_activation_code()
        send_activation_mail.delay(user.email, user.activation_code)
        return user


class ChangePasswordForm(forms.Form):
    old_pass = forms.CharField(widget=forms.PasswordInput)
    new_pass = forms.CharField(min_length=8, widget=forms.PasswordInput)
    new_pass_confirm = forms.CharField(min_length=8, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_old_pass(self):
        old_pass = self.cleaned_data.get('old_pass')
        user = self.request.user
        if not user.check_password(old_pass):
            raise forms.ValidationError('Enter the correct password')
        return old_pass

    def clean(self):
        new_pass = self.cleaned_data.get('new_pass')
        new_pass_confirm = self.cleaned_data.get('new_pass_confirm')
        if new_pass != new_pass_confirm:
            raise forms.ValidationError('Invalid password confirmation')
        return self.cleaned_data

    def save(self):
        new_pass = self.cleaned_data.get('new_pass')
        user = self.request.user
        user.set_password(new_pass)
        user.save()


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('User is not found')
        return email

    def send_new_password(self):
        email = self.cleaned_data.get('email')
        new_pass = get_random_string(length=8)
        user = User.objects.get(email=email)
        user.set_password(new_pass)
        user.save()
        send_mail('Password reset', f'Your new password: {new_pass}', 'test@gmail.com', [email])
