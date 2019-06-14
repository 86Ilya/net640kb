import os
import logging
import mimetypes

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from Net640.apps.images.forms import ImageForm
from Net640.apps.images.models import Image
from Net640.apps.user_profile.models import RELATIONSHIP_FRIENDS
from Net640.errors import NotEnoughSpace
from Net640.settings import MEDIA_ROOT


User = get_user_model()
logger = logging.getLogger(__name__)
users_media = os.path.join(MEDIA_ROOT, 'users')


@login_required
@require_http_methods(["GET", "POST"])
def user_images_view(request):
    """
    This view gives us a page with images album of logged user.
    In POST method this view will add new image.
    """
    master = request.user

    images = []
    for image in Image.objects.filter(user=master):
        images.append({'url': image.image.url,
                       'description': image.description,
                       'id': image.id,
                       'user_has_like': image.has_like(master),
                       'rating': image.get_rating(),
                       'width': image.image.width})

    if request.method == 'POST':
        image_form = ImageForm(request.POST, request.FILES, user=request.user)
        if image_form.is_valid():
            try:
                image = image_form.save(commit=False)
                image.user = master
                image.save()
            except NotEnoughSpace:
                pass
            return redirect('user_images')
    else:
        image_form = ImageForm()
    return render(request, 'user_images.html', {
        'image_form': image_form,
        'username': master.username,
        'images': images
    })


@login_required
@require_POST
def user_image_action(request):
    context = {}
    user = request.user
    image_id = request.POST.get('image_id', None)
    image = get_object_or_404(Image, id=image_id)
    action = request.POST.get('action', None)

    if action == 'like':
        image.add_like(user)
        context.update({"result": True, "likes": image.get_rating()})
    if action == 'dislike':
        image.remove_like(user)
        context.update({"result": True, "likes": image.get_rating()})
    if action == 'remove':
        if user == image.user:
            image.delete()
            context.update({"result": True})
    return JsonResponse(context)


@require_GET
def get_image(request, username, imagename):
    """
    This function are working in cooperation with Nginx.
    Function is checking permission on requested resource before giving it to user.
    """
    master = request.user
    user = get_object_or_404(User, username=username)
    if master == user or master.check_relationship(user) == RELATIONSHIP_FRIENDS:
        file_on_disk = os.path.join(users_media, username, imagename)
        file_size = os.path.getsize(file_on_disk)
        content_type, _ = mimetypes.guess_type(imagename)
        response = HttpResponse()
        response.status_code = 200
        response['X-Accel-Redirect'] = request.path
        response['Content'] = content_type
        response['Content-length'] = file_size
    else:
        response = HttpResponseNotFound("File not found:{}".format(imagename))
    return response
