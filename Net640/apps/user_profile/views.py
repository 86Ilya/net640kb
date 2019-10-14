from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods, require_GET

from Net640.httpcodes import HTTP_BAD_REQUEST, HTTP_OK, HTTP_UNAUTHORIZED
from Net640.apps.user_profile.helpers import base, save_user_by_form, update_user_by_form, reset_password_for_email
from Net640.apps.user_profile.forms import UserForm, UserUpdateForm,\
    UserRequestPasswordResetForm, UserPasswordUpdateForm
from Net640.apps.user_profile.models import DEFAULT_AVATAR_URL, UserResetPassword
from Net640.apps.user_profile.exceptions import UserException


User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    context = base(request)
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('mainpage')
        else:
            context.update({'login_failed': True})
            return render(request, 'login.html', context, status=HTTP_UNAUTHORIZED)
    else:
        return render(request, "login.html", context)


@require_http_methods(["GET", "POST"])
def signup_view(request):
    context = base(request)
    status = HTTP_OK
    if request.method == "POST":
        signup_form, valid = save_user_by_form(request, context)
        context.update({'signup_form': signup_form})
        if valid:
            return render(request, 'signup_code_was_sent.html', {'error': None}, status=status)
        else:
            status = HTTP_BAD_REQUEST
    else:
        signup_form = UserForm
        context.update({'signup_form': signup_form})

    return render(request, 'signup.html', context, status=status)


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    context = base(request)
    status = HTTP_OK
    if request.method == "POST":
        action = request.POST.get('action', None)
        if action:
            response, status = profile_view_action_processing(request, action)
            return JsonResponse(response, status=status)
        user_update_form, valid = update_user_by_form(request, context)
        if not valid:
            status = HTTP_BAD_REQUEST
    else:
        user_update_form = UserUpdateForm(initial={'firstname': context['user'].firstname,
                                                   'lastname': context['user'].lastname,
                                                   'patronymic': context['user'].patronymic,
                                                   'birth_date': context['user'].birth_date})
        login(request, context['user'])
    context.update({'update_form': user_update_form})
    return render(request, 'profile.html', context, status=status)


def profile_view_action_processing(request, action):
    status = HTTP_OK
    user = request.user
    if action == 'remove_avatar':
        avatar_size = user.avatar.size
        user.remove_avatar()
        if avatar_size:
            # send decrement info
            user.msg_upd_page_size(-avatar_size)
            response = {'result': True, 'default_avatar_url': DEFAULT_AVATAR_URL}
    else:
        response = {'result': False, 'error': 'unknown action'}
        status = HTTP_BAD_REQUEST
    return response, status


@login_required
@require_GET
def logout_view(request):
    logout(request)
    return redirect('mainpage')


@require_http_methods(["GET"])
def signup_confirm(request, user_id, confirmation_code):
    status = HTTP_OK
    context = {'confirmed': False}
    user = get_object_or_404(User, id=user_id)
    if not user.is_active:
        if user.get_activation_code() == confirmation_code:
            user.is_active = True
            user.save()
            context.update({'confirmed': True})
        else:
            status = HTTP_BAD_REQUEST
            context.update({'reason': 'Confirmation code is incorrect'})
    else:
        return redirect('login')

    return render(request, 'signup_confirm.html', context, status=status)


@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    password_reset_request_form = UserRequestPasswordResetForm()
    context = {'reset_password_form': password_reset_request_form}

    if request.method == "POST":
        email = request.POST['email']
        try:
            reset_password_for_email(email)
            context.update({'info': 'Link was sent to your email'})
        except Exception as error:
            context.update({'error': error})

    return render(request, "password_reset_request.html", context)


@require_http_methods(["GET", "POST"])
def password_reset(request, user_id, confirmation_code):
    status = HTTP_OK
    password_update_form = UserPasswordUpdateForm()
    context = {'reset': False}
    context.update({'password_update_form': password_update_form})

    if request.method == "GET":
        user = get_object_or_404(User, id=user_id)
        if not user.is_active:
            context.update({'error': 'Account is not activated. Visit activation link first.'})
        else:
            try:
                reset_code = user.get_password_reset_code()
                if reset_code != confirmation_code:
                    context.update({'error': 'Reset code is incorrect'})
            except UserException as error:
                context.update({'error': error})

    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        if user.is_active and user.get_password_reset_code() == confirmation_code:
            password_update_form = UserPasswordUpdateForm(request.POST, instance=user)
            if password_update_form.is_valid():
                user_update = password_update_form.save(commit=False)
                user_update.save()
                # delete record about reset code from db
                UserResetPassword.objects.get(user=user).delete()
                context.update({'info': 'Password successfully changed'})
            else:
                context.update({'password_update_form': password_update_form})

    return render(request, 'password_reset.html', context, status=status)
