from django.contrib.auth.decorators import login_required


@login_required
def user_post_action(request, post_id, action):
    pass
