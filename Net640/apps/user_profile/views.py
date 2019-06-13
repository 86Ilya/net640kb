from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods, require_GET

from Net640.apps.user_posts.models import Post
from Net640.apps.user_profile.forms import UserForm, UserUpdateForm
from Net640.apps.user_posts.forms import PostForm
from Net640.httpcodes import HTTP_BAD_REQUEST, HTTP_OK, HTTP_UNAUTHORIZED
from Net640.errors import NotEnoughSpace
from Net640.apps.user_profile.helpers import base, save_user_by_form, update_user_by_form

User = get_user_model()


@require_http_methods(["GET", "POST"])
def mainpage_view(request):
    user_login = check_user_auth(request.user)
    context = {'user_login': user_login}

    if user_login:
        master = request.user
        posts = list()
        if request.method == "POST":
            post_form = PostForm(request.POST, request.FILES, user=request.user)
            if post_form.is_valid():
                try:
                    new_post = post_form.save(commit=False)
                    new_post.user = request.user
                    new_post.save()
                except NotEnoughSpace:
                    pass
                else:
                    post_form = PostForm
        else:
            post_form = PostForm

        for post in Post.objects.filter(user=master)[:10]:
                posts.append({'content': post.content,
                              'user_has_like': post.has_like(master),
                              'rating': post.get_rating(),
                              'author': post.user,
                              'date': post.date,
                              'image_url': post.get_image_url(),
                              'id': post.id, })

        context.update({'posts': posts, 'post_form': post_form, 'firstname': request.user.firstname})
        return render(request, 'main_page.html', context)
    else:
        return render(request, 'info.html')


def check_user_auth(user):
    return user.is_authenticated


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
