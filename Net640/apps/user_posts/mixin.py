from django.urls import reverse
from Net640.settings import FRONTEND_DATE_FORMAT


class AsDictMessageMixin:
    """
    Mixin for representing user messages(post, comments) as dictionaries

    """
    def as_dict(self, executor):
        return {'content': self.content,
                'user_has_like': self.has_like(executor),
                'is_owner': self.user == executor,
                'rating': round(self.get_rating(), 1),
                'author': self.user.username,
                'author_page': reverse('friends:user_view', kwargs={'user_id': self.user.id}),
                'date': self.date.strftime(FRONTEND_DATE_FORMAT),
                'id': self.id,
                'author_thumbnail_url': self.user.get_thumbnail_url(), }
