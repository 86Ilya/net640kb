from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView)
from django.urls import reverse_lazy
from django.conf import settings

from Net640.apps.user_profile.forms import UserRequestPasswordResetForm, UserPasswordResetConfirmForm


class Net640PasswordResetView(PasswordResetView):
    form_class = UserRequestPasswordResetForm
    template_name = 'password_reset_request.html'
    success_url = reverse_lazy('profile:password_reset_done')
    email_template_name = 'password_reset_email.html'
    from_email = settings.DEFAULT_FROM_EMAIL


class Net640PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class Net640PasswordResetConfirmView(PasswordResetConfirmView):
    form_class = UserPasswordResetConfirmForm
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('profile:password_reset_complete')


class Net640PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
