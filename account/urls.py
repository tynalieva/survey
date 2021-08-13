from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

# urlpatterns = [
#     path('register/', views.RegistrationView.as_view(), name='register'),
#     path('login/', views.LoginView.as_view(), name='login'),
#     path('logout/', views.LogoutView.as_view(), name='logout'),
#     path('', login_required(views.HomeView.as_view()), name='home'),
#     path('activate/<uidb64>/<token>', views.ActivateView.as_view(), name='activate'),
#     path('reset_password', views.ResetPassword.as_view(), name='reset_password'),
#     path('set_new_password/<uidb64>/<token>', views.SetNewPasswordView.as_view(), name='set_new_password'),
#
# ]
from django.contrib.auth.views import LogoutView
from django.urls import path

from account.views import *

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('register_activate/<uuid:activation_code>/', ActivationView.as_view(), name='register_activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('reset_password/', ForgotPasswordView.as_view(), name='reset_password'),
    path('profile/', profile, name='profile'),
]