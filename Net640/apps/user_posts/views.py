from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, reverse
from django.views.decorators.http import require_http_methods

from Net640.apps.user_posts.models import Comment
from Net640.apps.user_posts.forms import PostForm, CommentForm
from Net640.apps.user_posts.helpers import user_comment_process_action_post, user_post_process_action_post
from Net640.apps.user_posts.helpers import user_news_processing_post_action
from Net640.apps.user_profile.helpers import base


@require_http_methods(["GET", "POST"])
def mainpage_view(request):
    context = base(request)
    context['explicit_processing_url'] = None

    if context['user']:
        post_form = PostForm()
        if request.method == "POST":
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
        context.update({'comment_form': CommentForm()})
        context.update({'posts': [], 'post_form': post_form})
        return render(request, 'main_page.html', context)
    else:
        return render(request, 'info.html')


@require_http_methods(["GET", "POST"])
def user_post_processing(request, user_id=None):
    """
    Function for processing all actions on user posts
    """
    result = dict()
    if request.method == "POST":
        # possible actions are: like, dislike, remove the post
        result = user_post_process_action_post(request, user_id)
    # TODO There will be method for processing creation of new post

    return JsonResponse(result)


@login_required
@require_http_methods(["GET", "POST"])
def user_news(request):
    context = {'explicit_processing_url': reverse('user_news')}

    if request.method == "POST":
        result = user_news_processing_post_action(request)
        return JsonResponse(result)

    return render(request, 'news.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def user_comment_processing(request, post_id=None):
    """
    Function for processing all actions on user comments
    """
    if request.method == "POST":
        # possible actions are: like, dislike, remove the comment, add a new comment
        result = user_comment_process_action_post(request)
    else:
        # get request returns the list of comments
        result = {'comments': [obj.as_dict(request.user) for obj in Comment.objects.filter(post_id=post_id)]}

    return JsonResponse(result)
