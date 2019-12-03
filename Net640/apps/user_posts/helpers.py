"""
This module contains auxiliary functions in order not to contaminate the view module with extra code
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from Net640.apps.user_posts.models import Comment, Post
from Net640.apps.user_posts.forms import CommentForm
from Net640.apps.user_profile.models import RELATIONSHIP_FRIENDS

User = get_user_model()

news_query = "select user_posts_post.id from user_posts_post\
                left join user_profile_relationship on user_profile_relationship.to_person_id=user_posts_post.user_id\
                where user_profile_relationship.status = %s and user_profile_relationship.from_person_id = %s\
                order by user_posts_post.date DESC"


def create_comment_from_request(request, context):
    user = request.user
    if user is None:
        return
    post_id = request.POST["post_id"]
    post = get_object_or_404(Post, id=post_id)
    comment_form = CommentForm(request.POST)

    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.user = user
        comment.post = post
        comment.save()
        context['result'] = True
        context['comment_meta_data'] = comment.as_dict(user)
        del context['comment_meta_data']['content']  # User already have the comment content on frontend
        return
    # in case of incorrect form set errors to the context
    context['errors'] = comment_form.errors


def user_comment_process_action_post(request):
    """
    Function for processing user comment with POST request
    """
    user = request.user
    context = {"result": False}
    comment_id = request.POST.get('id', None)

    if comment_id:
        comment = get_object_or_404(Comment, id=comment_id)
        action = request.POST.get('action', None)
        if action == 'like':
            comment.add_like(user)
            context.update({"result": True, "likes": comment.get_rating()})
            return context
        if action == 'dislike':
            comment.remove_like(user)
            context.update({"result": True, "likes": comment.get_rating()})
            return context
        if action == 'remove':
            if user == comment.user:
                comment.delete()
                context.update({"result": True})
            return context

    # if there is no action, then try to create a new comment
    create_comment_from_request(request, context)
    return context


def user_post_process_action_post(request, user_id):
    """
    Function for processing user post with POST request
    """
    context = {"result": False}
    user = request.user
    post_id = request.POST.get('id', None)
    action = request.POST.get('action', None)
    if post_id:
        post = get_object_or_404(Post, id=post_id)
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
    # if there is no post_id, we will try to find all messages by user ID
    if action == 'get_posts':
        posts = list()
        if not user_id:
            from_user = user
        else:
            from_user = get_object_or_404(User, id=user_id)
        for post in Post.objects.filter(user=from_user):
            posts.append(post.as_dict(user))
        context.update({"result": True, "posts": posts})
    return context


def user_news_processing_post_action(request):
    """
    Function for processing user news with POST request
    """
    master = request.user
    action = request.POST["action"]
    result = {'status': False}
    posts = list()
    # get news
    if action == "get_posts":
        for post in Post.objects.raw(news_query, [RELATIONSHIP_FRIENDS, master.id]):
            posts.append(post.as_dict(master))
        result = {'posts': posts,
                  'status': True}
    else:
        # incorrect operation
        pass
    return result
