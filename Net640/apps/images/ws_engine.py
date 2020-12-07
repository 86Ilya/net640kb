from django.contrib.auth import get_user_model

from Net640.apps.images.models import Image

User = get_user_model()


def clean_image_and_user(func):
    def wrapped_func(self, user, message):
        try:
            id = message['image_id']
            image = Image.objects.get(id=id)
        except Image.DoesNotExist:
            return {"result": False, "error": "image doesn't exist"}
        return func(self, user, image)
    return wrapped_func


class ImageProcessing:

    def __call__(self, user, message):
        # TODO: try..except
        func = getattr(self, message['action'])
        return func(user, message)

    @clean_image_and_user
    def like(self, user, image):
        image.add_like(user)
        return {"result": True,
                "action": "like",
                "image_id": image.id,
                "likes": image.get_rating()}

    @clean_image_and_user
    def dislike(self, user, image):
        image.remove_like(user)
        return {"result": True,
                "action": "dislike",
                "image_id": image.id,
                "likes": image.get_rating()}

    @clean_image_and_user
    def remove(self, user, image):
        if user != image.user:
            return {"result": False, "error": "The image belongs to another user"}

        image_id = image.id
        image.delete()
        return {"result": True,
                "action": "remove",
                "image_id": image_id}
