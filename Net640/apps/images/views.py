from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from Net640.apps.images.forms import ImageForm
from Net640.apps.user_profile.models import Image
from Net640.httpcodes import HTTP_BAD_REQUEST, HTTP_OK, HTTP_UNAUTHORIZED
from Net640.errors import NotEnoughSpace

User = get_user_model()


@login_required
def user_images_view(request):
    master = request.user

    images = []
    for image in Image.objects.filter(user=master):
        images.append({'url': image.image,
                       'description': image.description,
                       'username': image.user.username,
                       'width': image.image.width})

    if request.method == 'POST':
        image_form = ImageForm(request.POST, request.FILES)
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
def get_image(request, user_id, image_name):
    user = User.objects.get(pk=user_id)
    path = 'id{}/images/{}'.format(user_id, image_name)
    # print path

    image = Image.objects.get(image=path)
    # print dir(image.image)
    return HttpResponse(
        image.image, content_type='image/jpg'
    )
