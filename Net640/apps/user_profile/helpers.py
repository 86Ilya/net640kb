from django.contrib.auth import get_user_model
from Net640.apps.user_profile.forms import UserForm, UserUpdateForm

User = get_user_model()


def base(request):
    """
    :param request:
    :return dict: Возвращает базовый контекст для всех страниц
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
    # context.update({'signup_form': user_form})
    if user_form.is_valid():
        valid = True
        user = user_form.save()
        user.save()
        context['user'] = user
    return user_form, valid


def update_user_by_form(request, context):
    user = context['user']
    valid = False
    user_update_form = UserUpdateForm(request.POST, request.FILES, instance=user)
    # context.update({'update_form': user_update_form})
    if user_update_form.is_valid():
        user_update = user_update_form.save(commit=False)
        user_update.save()
        context['user'] = user_update
        valid = True
    else:
        # This is strange but user instance is changed after form validation
        context['user'].refresh_from_db()
    return user_update_form, valid
