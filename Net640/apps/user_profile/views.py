from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
# from django.core.exceptions import ObjectDoesNotExist

from Net640.apps.user_posts.models import Post
from Net640.apps.user_profile.forms import UserForm, UserUpdateForm
from Net640.apps.user_posts.forms import PostForm
from Net640.httpcodes import HTTP_BAD_REQUEST, HTTP_OK, HTTP_UNAUTHORIZED
from Net640.errors import NotEnoughSpace
from Net640.apps.user_profile.helpers import base, save_user_by_form, update_user_by_form

User = get_user_model()


def mainpage_view(request):
    user_login = check_user_auth(request.user)
    context = {'user_login': user_login}

    if user_login:
        if request.method == "POST":
            post_form = PostForm(request.POST, user=request.user)
            if post_form.is_valid():
                try:
                    new_post = post_form.save(commit=False)
                    new_post.author = request.user
                    new_post.save()
                except NotEnoughSpace:
                    pass
                else:
                    post_form = PostForm
        else:
            post_form = PostForm

        posts = Post.objects.filter(author=request.user)[:10]
        context.update({'posts': posts, 'post_form': post_form, 'firstname': request.user.firstname})
        return render(request, 'main_page.html', context)
    else:
        return render(request, 'info.html')


def check_user_auth(user):
    return user.is_authenticated


# FOR DEBUG ONLY
@login_required
def all_users(request):
    friends = User.objects.all()
    ctx = {'firstname': request.user.firstname,
           'friends': friends}

    return render(request, 'friends.html', ctx)


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


def signup_view(request):
    context = base(request)
    status = HTTP_OK
    if request.method == "POST":
        signup_form, valid = save_user_by_form(request, context)
        context.update({'signup_form': signup_form})
        # breakpoint()
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
def profile_view(request):
    context = base(request)
    status = HTTP_OK
    if request.method == "POST":
        user_update_form, valid = update_user_by_form(request, context)
        # breakpoint()
        if not valid:
            status = HTTP_BAD_REQUEST
    else:
        user_update_form = UserUpdateForm(initial={'firstname': context['user'].firstname,
                                                   'lastname': context['user'].lastname,
                                                   'patronymic': context['user'].patronymic,
                                                   'birth_date': context['user'].birth_date})
        login(request, context['user'])  # TODO ???
        # breakpoint()
    context.update({'update_form': user_update_form})
    return render(request, 'profile.html', context, status=status)


@login_required
def logout_view(request):
    logout(request)
    return redirect('mainpage')


