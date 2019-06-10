from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from Net640.apps.user_posts.models import Post
from Net640.apps.user_profile.models import RELATIONSHIP_FRIENDS

news_query = "select user_posts_post.id from user_posts_post\
                left join user_profile_relationship on user_profile_relationship.to_person_id=user_posts_post.author_id\
                where user_profile_relationship.status = %s and user_profile_relationship.from_person_id = %s\
                order by user_posts_post.date DESC"


@login_required
def user_post_action(request):
    context = {}
    user = request.user
    if request.method == "POST":
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
            if user == post.author:
                post.delete()
                context.update({"result": True})
        return JsonResponse(context)


@login_required
def user_news(request):
    master = request.user
    context = dict()

    if request.method == "POST":
        result = user_news_post_action(master, request.POST)
        return JsonResponse(result)

    return render(request, 'news.html', context)


def user_news_post_action(master, post):
    action = post["action"]
    result = {'status': False}
    posts = list()
    # get news
    if action == "get_news":
        for post in Post.objects.raw(news_query, [master.id, RELATIONSHIP_FRIENDS])[:10]:
                posts.append({'content': post.content,
                              'user_has_like': post.has_like(master),
                              'rating': round(post.get_rating(), 1),
                              'author': post.author.username,
                              # TODO reverse link
                              'author_page': '/id' + str(post.author.id),
                              'date': post.date.strftime('%b %d, %Y'),
                              'id': post.id,
                              'author_thumbnail_url': post.author.get_thumbnail_url(), })

        result = {'posts': posts,
                  'status': True}
    else:
        # incorrect operation
        pass
    return result
