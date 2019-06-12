from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from Net640.apps.user_posts.models import Post

User = get_user_model()


@login_required
@require_http_methods(["GET", "POST"])
def friends_view(request):
    master = User.objects.get(pk=request.user.id)
    if request.method == "POST" and request.POST.get("action", False):
        return JsonResponse(friends_view_post_action(master, request.POST))

    friends = master.get_friends()
    waiting_for_accept = master.get_waiting_for_accept()
    sended_requests = master.get_requests_for_relationship()

    context = {'username': master.username,
               'friends': friends,
               'waiting_for_accept': waiting_for_accept,
               'sended_requests': sended_requests
               }

    return render(request, 'friends.html', context)


def friends_view_post_action(master, post):
    person = None
    action = post["action"]
    user_id = post.get("user_id", False)
    result = {'status': False}

    if user_id:
        person = User.objects.get(pk=user_id)
    # Получим список друзей и заявок
    if person and action == "cancel":
        result = master.cancel(person)

    elif person and action == "accept":
        result = master.accept(person)

    elif action == "get_friends_lists":
        friends, waiting_for_accept, sended_requests = master.get_friends_lists()
        result = {
            'friends_list': friends,
            'friends_waiting_for_accept_list': waiting_for_accept,
            'friends_sent_requests_list': sended_requests}
    else:
        # incorrect operation
        pass
    return result


@login_required
@require_http_methods(["GET", "POST"])
def user_view(request, user_id):
    master = User.objects.get(pk=request.user.id)
    if int(user_id) == master.id:
        return redirect('mainpage')

    page_owner = User.objects.get(pk=user_id)
    relationship_status = master.check_relationship(page_owner)
    if request.method == "POST" and request.POST.get("action", False):
        result = user_view_post(master, page_owner, request.POST)
        return JsonResponse(result)

    context = {
                'relationship_status': relationship_status,
                'page_owner_username': page_owner.username,
                'page_owner_id': page_owner.id,
                'page_owner_size': page_owner.get_size(),
                'user': master,
              }
    return render(request, 'user_view.html', context)


def user_view_post(master, page_owner, post):
    action = post["action"]
    result = {'status': False}
    if action == "add":
        # Отправим запрос на добавление пользователя в друзья
        result = master.accept(page_owner)
    # Получим информацию о пользователе (статус отношении, посты)
    elif action == "get_user_info":
        relationship_status = master.check_relationship(page_owner)
        posts = []
        for post in Post.objects.filter(author=page_owner)[:10]:
                posts.append({'content': post.content,
                              'user_has_like': post.has_like(master),
                              'rating': round(post.get_rating(), 1),
                              'author': post.author.username,
                              'author_id': post.author.id,
                              'date': post.date.strftime('%b %d, %Y'),
                              'id': post.id,
                              'author_thumbnail_url': post.author.get_thumbnail_url(), })
        result = {'relationship_status': relationship_status,
                  'posts': posts,
                  'page_owner': {'id': page_owner.id, 'username': page_owner.username},
                  'status': True}
    else:
        # incorrect operation
        pass
    return result
