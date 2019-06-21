from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods, require_GET

from Net640.httpcodes import HTTP_BAD_REQUEST, HTTP_OK, HTTP_UNAUTHORIZED
from Net640.apps.user_profile.helpers import base, save_user_by_form, update_user_by_form
from Net640.apps.user_profile.forms import UserForm, UserUpdateForm
from Net640.apps.user_profile.models import DEFAULT_AVATAR_URL
from Net640.apps.updateflow.helpers import get_updateflow_room_name


User = get_user_model()
CHANNEL_LAYER = get_channel_layer()


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
            login(request, context['user'])
            return redirect('mainpage')
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
        if action == 'remove_avatar':
            avatar_size = request.user.avatar.size
            request.user.remove_avatar()
            if avatar_size:
                # send decrement info
                response = {'dec_user_page_size': avatar_size, 'error': False}
                room_name = get_updateflow_room_name(request.user.id)
                async_to_sync(CHANNEL_LAYER.group_send)(room_name, {
                    'type': 'update_flow',
                    'message': response
                })

            return JsonResponse({'result': True, 'default_avatar_url': DEFAULT_AVATAR_URL})
        user_update_form, valid = update_user_by_form(request, context)
        if not valid:
            status = HTTP_BAD_REQUEST
    else:
        user_update_form = UserUpdateForm(initial={'firstname': context['user'].firstname,
                                                   'lastname': context['user'].lastname,
                                                   'patronymic': context['user'].patronymic,
                                                   'birth_date': context['user'].birth_date})
        login(request, context['user'])  # TODO ???
    context.update({'update_form': user_update_form})
    return render(request, 'profile.html', context, status=status)


@login_required
@require_GET
def logout_view(request):
    logout(request)
    return redirect('mainpage')
