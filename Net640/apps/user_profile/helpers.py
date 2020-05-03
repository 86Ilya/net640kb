import logging

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from Net640.apps.user_profile.forms import UserForm, UserUpdateForm
from Net640.apps.user_profile.exceptions import UserException

User = get_user_model()


def check_user_auth(user):
    return user.is_authenticated


def base(request):
    """
    :param request:
    :return dict: return base context
    """
    context = dict()
    if not request.user.is_anonymous:
        user = User.objects.get(pk=request.user.pk)
        context.update({"user": user})
    else:
        context.update({"user": None})
    return context


def save_user_by_form(request, context):
    valid = False
    user_form = UserForm(request.POST, request.FILES)

    if user_form.is_valid():
        valid = True
        try:
            user = user_form.save()
        except UserException as error:
            logging.error(f"Error occured while saving user from form: {error}")
            user_form.valid = False
            # add error to user form
            user_form.errors.update({"__all__": str(error)})
            return user_form, False

        context['user'] = user
    return user_form, valid


def update_user_by_form(request, context):
    user = context['user']
    valid = False
    user_update_form = UserUpdateForm(request.POST, request.FILES, instance=user)
    if user_update_form.is_valid():
        user_update = user_update_form.save(commit=False)
        user_update.save()
        context['user'] = user_update
        valid = True
    else:
        # This is strange but user instance is changed after form validation
        context['user'].refresh_from_db()
    return user_update_form, valid


def reset_password_for_email(email):
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        raise UserException(_("User doesn't exist"))

    if user:
        try:
            user.send_reset_password_link()
        except Exception:
            raise UserException(_("Something went wrong"))
