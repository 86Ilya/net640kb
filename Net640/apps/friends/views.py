from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from Net640.apps.user_posts.forms import CommentForm

User = get_user_model()


@login_required
@require_http_methods(["GET", "POST"])
def friends_view(request):
    """
    This view renders page that shows all friend and all requests for relationship
    """
    master = User.objects.get(pk=request.user.id)
    if request.method == "POST" and request.POST.get("action", False):
        return JsonResponse(friends_view_post_action(master, request.POST))

    # our friends.
    friends = master.get_friends()
    # requests from another person's
    waiting_for_accept = master.get_waiting_for_accept()
    # requests that we had send for new relationships
    sended_requests = master.get_requests_for_relationship()

    context = {'username': master.username,
               'friends': friends,
               'waiting_for_accept': waiting_for_accept,
               'sended_requests': sended_requests
               }

    return render(request, 'friends.html', context)


def friends_view_post_action(master, post):
    """
    Process any action on modifying relationship:
     - send request for relationship
     - accept request
     - remove friend
    """
    person = None
    action = post["action"]
    user_id = post.get("user_id", False)
    result = {'status': False}

    if user_id:
        person = User.objects.get(pk=user_id)
    # Get list of all our friends
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
    """
    This view shows to us personal page of somebody
    """
    master = User.objects.get(pk=request.user.id)
    if int(user_id) == master.id:
        return redirect('posts:mainpage')
    page_owner = User.objects.get(pk=user_id)
    relationship_status = master.check_relationship(page_owner)
    if request.method == "POST" and request.POST.get("action", False):
        result = user_view_post(master, page_owner, request.POST)
        return JsonResponse(result)

    context = {
        'relationship_status': relationship_status,
        'page_owner_username': page_owner.username,
        'page_owner_id': page_owner.id,
        'page_owner_chat_url': page_owner.get_chat_url(),
        'page_owner_size': page_owner.get_size(),
        'user': master,
        'comment_form': CommentForm(),
        'explicit_processing_url': reverse('posts:user_post_processing', kwargs={'user_id': user_id}),
    }
    return render(request, 'user_view.html', context)


# TODO move to rest api
def user_view_post(master, page_owner, post):
    action = post["action"]
    result = {'status': False}
    if action == "add":
        # Send request for adding to friends
        result = master.accept(page_owner)
    # Get information about user (relationship status, ...)
    elif action == "get_user_info":
        relationship_status = master.check_relationship(page_owner)
        result = {'relationship_status': relationship_status,
                  'page_owner': {'id': page_owner.id,
                                 'url': page_owner.get_page_url(),
                                 'username': page_owner.username},
                  'status': True}
    else:
        # incorrect operation
        pass
    return result
