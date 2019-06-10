import os
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from Net640.apps.images.forms import ImageForm
from Net640.apps.images.models import Image
from Net640.apps.user_profile.models import RELATIONSHIP_FRIENDS
from Net640.errors import NotEnoughSpace

User = get_user_model()
logger = logging.getLogger(__name__)


@login_required
def user_images_view(request):
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
def user_image_action(request):
    context = {}
    user = request.user
    if request.method == "POST":
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


def get_image(request, username, imagename):
    master = request.user
    user = get_object_or_404(User, username=username)
    if master == user or master.check_relationship(user) == RELATIONSHIP_FRIENDS:
        # TODO remove hardcode
        file_on_disk = '/app' + request.path
        file_size = os.path.getsize(file_on_disk)
        file_type = file_on_disk.split('.')[-1].lower()
        if file_type == 'jpg':
            content_type = 'image/jpg'
        elif file_type == 'png':
            content_type = 'image/png'
        else:
            content_type = ''

        response = HttpResponse()
        response.status_code = 200
        response['X-Accel-Redirect'] = request.path
        response['Content'] = content_type
        response['Content-length'] = file_size
    else:
        response = Http404
    return response
