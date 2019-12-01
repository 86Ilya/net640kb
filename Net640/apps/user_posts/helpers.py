"""
This module contains auxiliary functions in order not to contaminate the view module with extra code
"""

from django.shortcuts import get_object_or_404
from Net640.apps.user_posts.models import Comment, Post
from Net640.apps.user_posts.forms import CommentForm


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
