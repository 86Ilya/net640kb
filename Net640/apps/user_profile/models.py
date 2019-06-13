import os
import logging
from PIL import Image as ImagePic
from channels.layers import get_channel_layer

from django.db import models, connection
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

from Net640.settings import STATIC_URL
from Net640.apps.images.models import Image, user_avatar_path
from Net640.apps.user_posts.models import Post


DEFAULT_AVATAR_URL = os.path.join(STATIC_URL, 'img', 'default_avatar.png')
DEFAULT_THUMBNAIL_URL = os.path.join(STATIC_URL, 'img', 'default_thumbnail.png')

RELATIONSHIP_REQUEST_HAS_SENT = 0
RELATIONSHIP_WAITING_FOR_ACCEPT = 1
RELATIONSHIP_FRIENDS = 2
RELATIONSHIP_BLOCKED = 3
NO_RELATIONSHIP = -1

RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_WAITING_FOR_ACCEPT, 'Waiting'),
    (RELATIONSHIP_FRIENDS, 'Friends'),
    (RELATIONSHIP_BLOCKED, 'Blocked'),
)

CHANNEL_LAYER = get_channel_layer()


class GetSizeMixin:
    """
    Class helper to calculate size of User data
    """
    def get_size(self):
        size = 0
        id = self.id
        cursor = connection.cursor()

        # own page
        cursor.execute('SELECT octet_length(t.*::text) FROM user_profile_user AS t WHERE t.id=%s;', [id, ])
        size += cursor.fetchone()[0]
        # posts
        cursor.execute('select sum(length) from (\
            SELECT octet_length(t.*::text) as "length" FROM user_posts_post AS t\
            WHERE t.user_id=%s )posts_sum', [id, ])
        posts_size = cursor.fetchone()[0]
        if posts_size:
            size += posts_size
        # posts images
        posts = Post.objects.filter(user_id=id)
        for post in posts:
            if post.image:
                size += post.image.size
        # posts likes
        cursor.execute('select sum(length) from (SELECT octet_length(t.*::text) as "length" FROM\
                           user_posts_post_likes AS t WHERE t.user_id=1)user_posts_likes;', [id, ])
        posts_likes_size = cursor.fetchone()[0]
        if posts_likes_size:
            size += posts_likes_size
        # messages
        cursor.execute('select sum(length) from (\
            SELECT octet_length(t.*::text) as "length" FROM chat_message AS t\
            WHERE t.author_id=%s )message_sum', [id, ])
        messages_size = cursor.fetchone()[0]
        if messages_size:
            size += messages_size

        # images
        images = Image.objects.filter(user_id=id)
        for image_obj in images:
            size += image_obj.image.size

        # images additional info in DB
        cursor.execute('select sum(length) from (\
            SELECT octet_length(t.*::text) as "length" FROM images_image AS t\
            WHERE t.user_id=%s)images_additional_info_sum', [id, ])
        images_info_size = cursor.fetchone()[0]
        if images_info_size:
            size += images_info_size
        # images likes
        cursor.execute('select sum(length) from (SELECT octet_length(t.*::text) as "length" FROM\
                           images_image_likes AS t WHERE t.user_id=1)user_images_likes;', [id, ])
        images_likes_size = cursor.fetchone()[0]
        if images_likes_size:
            size += images_likes_size
        # avatar
        if self.avatar:
            size += self.avatar.size

        return size


class User(AbstractBaseUser, PermissionsMixin, GetSizeMixin):
    username = models.CharField(_('username'), unique=True, max_length=120, null=True)
    email = models.EmailField(_('email address'), unique=True)
    firstname = models.CharField(_('first name'), max_length=120, null=True)
    lastname = models.CharField(_('last name'), max_length=120, null=True, blank=True)
    patronymic = models.CharField(_('patronymic'), max_length=120, null=True, blank=True)
    birth_date = models.DateField(_('birth date'), null=True, blank=True)
    relationships = models.ManyToManyField('self', through='Relationship',
                                           symmetrical=False,
                                           related_name='related_to+')
    is_active = models.BooleanField(default=True)  # default=False when you are going to implement Activation Mail
    is_admin = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=user_avatar_path, default=None)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_thumbnail()

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return DEFAULT_AVATAR_URL

    def get_thumbnail_url(self):
        if self.avatar:
            return self.avatar.url.split(".")[0] + "_thumbnail.png"
        else:
            return DEFAULT_THUMBNAIL_URL

    def create_thumbnail(self):
        # If there is no image associated with this.
        # do not create thumbnail
        if not self.avatar:
            return

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (64, 64)

        im = ImagePic.open(self.avatar.file.name)
        im.thumbnail(THUMBNAIL_SIZE)
        im.save(self.avatar.file.name.split(".")[0] + "_thumbnail.png")

    def send_request_for_relationship(self, person):
        current_status = self.check_relationship(person)
        if current_status == NO_RELATIONSHIP:
            relationship, created = Relationship.objects.get_or_create(
                from_person=self,
                to_person=person,
                status=RELATIONSHIP_REQUEST_HAS_SENT)
        # if created:
            person.add_relationship(self, RELATIONSHIP_WAITING_FOR_ACCEPT, False)
            current_status = self.check_relationship(person)
        return current_status

    def accept_request_for_relationship(self, person):
        # remove old relationships
        self.remove_relationship(person, RELATIONSHIP_WAITING_FOR_ACCEPT, False)
        person.remove_relationship(self, RELATIONSHIP_REQUEST_HAS_SENT, False)
        # add new relationship
        self.add_relationship(person, RELATIONSHIP_FRIENDS)
        return self.check_relationship(person)

    def cancel_request_for_relationship(self, person):
        # Удалим запрос на добавление в друзья к себе
        self.remove_relationship(person, RELATIONSHIP_WAITING_FOR_ACCEPT, False)
        person.remove_relationship(self, RELATIONSHIP_REQUEST_HAS_SENT, False)
        return self.check_relationship(person)

    def cancel_sended_request(self, person):
        # Удалим отправленный запрос на добавление в друзья
        self.remove_relationship(person, RELATIONSHIP_REQUEST_HAS_SENT, False)
        person.remove_relationship(self, RELATIONSHIP_WAITING_FOR_ACCEPT, False)
        # return True
        return self.check_relationship(person)

    def add_relationship(self, person, status, symm=True):
        relationship, created = Relationship.objects.get_or_create(
            from_person=self,
            to_person=person,
            status=status)
        if symm:
            # avoid recursion by passing `symm=False`
            person.add_relationship(self, status, False)
        if not created:
            relationship.save()
        # return relationship
        return self.check_relationship(person)

    def remove_relationship(self, person, status, symm=True):
        Relationship.objects.filter(
            from_person=self,
            to_person=person,
            status=status).delete()
        if symm:
            # avoid recursion by passing `symm=False`
            person.remove_relationship(self, status, False)
        # return True
        return self.check_relationship(person)

    def check_relationship(self, person):
        # TODO временно так!
        result = Relationship.objects.filter(
            from_person=self,
            to_person=person)
        if result:
            return result[0].status
        else:
            return -1

    def get_relationships(self, status):
        return self.relationships.filter(
            to_people__status=status,
            to_people__from_person=self)

    def get_friends(self):
        return self.get_relationships(RELATIONSHIP_FRIENDS)

    def get_waiting_for_accept(self):
        # return self.relationships.filter(
        #     to_people__status=RELATIONSHIP_WAITING_FOR_ACCEPT,
        #     from_people__to_person=self)
        return self.get_relationships(RELATIONSHIP_WAITING_FOR_ACCEPT)

    def get_requests_for_relationship(self):
        return self.get_relationships(RELATIONSHIP_REQUEST_HAS_SENT)

    def get_friends_lists(self):
        friends = list()
        waiting_for_accept = list()
        sended_requests = list()
        for profile in self.get_relationships(RELATIONSHIP_FRIENDS):
            friends.append({'id': profile.id, 'firstname': profile.firstname, 'username': profile.username})

        for profile in self.get_waiting_for_accept():
            waiting_for_accept.append({'id': profile.id, 'firstname': profile.firstname, 'username': profile.username})
        for profile in self.get_requests_for_relationship():
            sended_requests.append({'id': profile.id, 'firstname': profile.firstname, 'username': profile.username})

        return friends, waiting_for_accept, sended_requests

    def cancel(self, person):
        relationship = self.check_relationship(person)
        relationship_upd = None
        success = False
        try:

            # Cancel request from person to us for adding to friends
            if relationship == RELATIONSHIP_WAITING_FOR_ACCEPT:
                relationship_upd = self.cancel_request_for_relationship(person)
                success = True

            # Cancel our request for friends to person
            elif relationship == RELATIONSHIP_REQUEST_HAS_SENT:
                relationship_upd = self.cancel_sended_request(person)
                success = True

            # Delete from friends person
            elif relationship == RELATIONSHIP_FRIENDS:
                relationship_upd = self.remove_relationship(person, RELATIONSHIP_FRIENDS)
                success = True
        # TODO broad exception
        except Exception as error:
            logging.error(error)

        return {'status': success, 'relationship_status': relationship_upd}

    def accept(self, person):
        relationship = self.check_relationship(person)
        relationship_upd = None
        success = False

        try:
            # Confirm person request to us and add him to our friends
            if relationship == RELATIONSHIP_WAITING_FOR_ACCEPT:
                relationship_upd = self.accept_request_for_relationship(person)
                success = True
            # If we have no relationship with person then send request for him
            elif relationship == NO_RELATIONSHIP:
                relationship_upd = self.send_request_for_relationship(person)
                success = True
        # TODO broad exception
        except Exception as error:
            logging.error(error)

        return {'status': success, 'relationship_status': relationship_upd}

    def __str__(self):
        return self.username


class Relationship(models.Model):
    from_person = models.ForeignKey(User, related_name='from_people', on_delete=models.CASCADE)
    to_person = models.ForeignKey(User, related_name='to_people', on_delete=models.CASCADE)
    status = models.IntegerField(choices=RELATIONSHIP_STATUSES)
