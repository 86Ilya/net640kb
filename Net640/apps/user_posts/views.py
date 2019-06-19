from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods, require_POST

from Net640.apps.user_posts.models import Post
from Net640.apps.user_posts.forms import PostForm
from Net640.apps.user_profile.models import RELATIONSHIP_FRIENDS
from Net640.apps.user_profile.helpers import base

news_query = "select user_posts_post.id from user_posts_post\
                left join user_profile_relationship on user_profile_relationship.to_person_id=user_posts_post.user_id\
                where user_profile_relationship.status = %s and user_profile_relationship.from_person_id = %s\
                order by user_posts_post.date DESC"


@require_http_methods(["GET", "POST"])
def mainpage_view(request):
    context = base(request)

    if context['user']:
        post_form = PostForm()
        if request.method == "POST":
            action = request.POST.get('action', None)
            if action:
                result = mainpage_post_action(request, action)
                # TODO add serializer to user
                context.update({'user': {'username': context['user'].username, 'id': context['user'].id}})
                context.update(result)
                return JsonResponse(context)
            new_post_form = PostForm(request.POST, request.FILES, user=request.user)
            if new_post_form.is_valid():
                try:
                    new_post = new_post_form.save(commit=False)
                    new_post.user = request.user
                    new_post.save()
                except Exception:
                    pass
            else:
                # show form errors to user
                post_form = new_post_form
        context.update({'posts': [], 'post_form': post_form})
        return render(request, 'main_page.html', context)
    else:
        return render(request, 'info.html')


def mainpage_post_action(request, action):
    master = request.user
    posts = list()
    if action == 'get_own_posts':
        for post in Post.objects.filter(user=master)[:10]:
            posts.append(post.as_dict(master))
        return {'posts': posts}


@login_required
@require_POST
def user_post_action(request):
    context = {}
    user = request.user
    context.update({"result": False})
    post_id = request.POST.get('post_id', None)
    post = get_object_or_404(Post, id=post_id)
    action = request.POST.get('action', None)

    if action == 'like':
        post.add_like(user)
        context.update({"result": True, "likes": post.get_rating()})
    if action == 'dislike':
        post.remove_like(user)
        context.update({"result": True, "likes": post.get_rating()})
    if action == 'remove':
        if user == post.user:
            post.delete()
            context.update({"result": True})
    return JsonResponse(context)


@login_required
@require_http_methods(["GET", "POST"])
def user_news(request):
    master = request.user
    context = dict()

    if request.method == "POST":
        result = user_news_post_action(master, request.POST)
        return JsonResponse(result)

    return render(request, 'news.html', context)


def user_news_post_action(master, post_request):
    action = post_request["action"]
    result = {'status': False}
    posts = list()
    # get news
    if action == "get_news":
        for post in Post.objects.raw(news_query, [RELATIONSHIP_FRIENDS, master.id])[:10]:
            posts.append(post.as_dict(master))
        result = {'posts': posts,
                  'status': True}
    else:
        # incorrect operation
        pass
    return result
