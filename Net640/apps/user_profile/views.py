from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods, require_GET
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from Net640.httpcodes import HTTP_BAD_REQUEST, HTTP_OK, HTTP_UNAUTHORIZED
from Net640.apps.user_profile.helpers import base, save_user_by_form, update_user_by_form
from Net640.apps.user_profile.forms import UserForm, UserUpdateForm

from Net640.apps.user_profile.models import DEFAULT_AVATAR_URL
from Net640.apps.user_profile.tokens import account_activation_token


User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    context = base(request)
    context.update({'login_failed': False})
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('posts:mainpage')
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
            user = context['user']
            # send activation code
            subject = 'Activate Your Net640kb Account'
            current_site = get_current_site(request)
            message = render_to_string('profile_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            user.email_user(subject, message)
            return redirect('profile:account_activation_sent')
        else:
            status = HTTP_BAD_REQUEST
    else:
        signup_form = UserForm
        context.update({'signup_form': signup_form})

    return render(request, 'signup.html', context, status=status)


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """
    View/Update personal settings
    """
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
    context.update({'update_form': user_update_form, 'user_page_url': context['user'].get_page_url()})
    return render(request, 'profile.html', context, status=status)


def profile_view_action_processing(request, action):
    status = HTTP_OK
    user = request.user
    if action == 'remove_avatar':
        avatar_size = user.avatar_size
        user.remove_avatar()
        if avatar_size:
            # send decrement info
            user.msg_upd_page_size(-avatar_size)
            response = {'result': True, 'default_avatar_url': DEFAULT_AVATAR_URL}
    # TODO add avatar size calc
    else:
        response = {'result': False, 'error': 'unknown action'}
        status = HTTP_BAD_REQUEST
    return response, status


@login_required
@require_GET
def logout_view(request):
    logout(request)
    return redirect('posts:mainpage')


def signup_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('posts:mainpage')
    else:
        return render(request, 'profile_confirmed.html', context={'confirmed': False})


def signup_confirm_sent(request):
    return render(request, 'profile_activation_code_was_sent.html', context={'error': False})
