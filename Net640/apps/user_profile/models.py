import os
import logging
from PIL import Image as ImagePic
from channels.layers import get_channel_layer

from django.db import models, connection
from django.shortcuts import reverse
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.core.cache import cache

from Net640.settings import STATIC_URL, EMAIL_HOST_USER, CACHE_TIMEOUT
from Net640.apps.images.models import user_avatar_path
from Net640.apps.updateflow.mixin import UpdateFlowMixin


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

    def __cache(func):
        def wrapper(self, *args, **kwargs):
            var = cache.get(self.id)
            if var is None:
                var = func(self, *args, **kwargs)
                cache.set(self.id, var, CACHE_TIMEOUT)
            return var
        return wrapper

    @__cache
    def get_size(self):
        return self._get_size()

    def _get_size(self):
        size = 0
        id = self.id
        cursor = connection.cursor()
        cursor.callproc('total_used_space', (id,))
        size = cursor.fetchone()[0]
        return size


class User(AbstractBaseUser, PermissionsMixin, GetSizeMixin, UpdateFlowMixin):
    username = models.CharField(_('username'), unique=True, max_length=120, null=True)
    email = models.EmailField(_('email address'), max_length=256, unique=True)
    firstname = models.CharField(_('first name'), max_length=120, null=True)
    lastname = models.CharField(_('last name'), max_length=120, null=True, blank=True)
    patronymic = models.CharField(_('patronymic'), max_length=120, null=True, blank=True)
    birth_date = models.DateField(_('birth date'), null=True, blank=True)
    relationships = models.ManyToManyField('self', through='Relationship',
                                           symmetrical=False,
                                           related_name='related_to+')
    is_active = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=user_avatar_path, default=None, null=True)
    avatar_size = models.IntegerField(default=0, blank=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        app_label = 'user_profile'

    def save(self, *args, **kwargs):
        if self.avatar:
            self.avatar_size = self.avatar.size
        super().save(*args, **kwargs)
        self.create_thumbnail()

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return DEFAULT_AVATAR_URL

    def get_chat_url(self):
        return reverse('chat:chat_room', kwargs={'user_id': self.id})

    def get_page_url(self):
        return reverse('friends:user_view', kwargs={'user_id': self.id})

    def remove_avatar(self):
        os.remove(self.avatar.path)
        self.avatar = None
        self.avatar_size = 0
        self.save()

    def get_thumbnail_url(self):
        if self.avatar:
            return self.avatar.url.split(".")[0] + "_thumbnail.png"
        else:
            return DEFAULT_THUMBNAIL_URL

    def email_user(self, subject, message):
        send_mail(subject,
                  message,
                  EMAIL_HOST_USER,
                  [self.email],
                  fail_silently=False,
                  )

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
        # TODO make it cleaner
        # remove old relationships
        self.remove_relationship(person, RELATIONSHIP_WAITING_FOR_ACCEPT, False)
        self.remove_relationship(person, RELATIONSHIP_REQUEST_HAS_SENT, False)
        person.remove_relationship(self, RELATIONSHIP_REQUEST_HAS_SENT, False)
        person.remove_relationship(self, RELATIONSHIP_WAITING_FOR_ACCEPT, False)
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
        if status == RELATIONSHIP_WAITING_FOR_ACCEPT:
            # send information about new request to frontend
            self.send_info_about_new_request_to_friends(person)

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
        return self.get_relationships(RELATIONSHIP_WAITING_FOR_ACCEPT)

    def get_requests_for_relationship(self):
        return self.get_relationships(RELATIONSHIP_REQUEST_HAS_SENT)

    def get_friends_lists(self):
        friends = list()
        waiting_for_accept = list()
        sended_requests = list()
        for profile in self.get_relationships(RELATIONSHIP_FRIENDS):
            friends.append({'id': profile.id, 'firstname': profile.firstname,
                            'username': profile.username, 'url': profile.get_page_url()})
        for profile in self.get_waiting_for_accept():
            waiting_for_accept.append({'id': profile.id, 'firstname': profile.firstname,
                                       'username': profile.username, 'url': profile.get_page_url()})
        for profile in self.get_requests_for_relationship():
            sended_requests.append({'id': profile.id, 'firstname': profile.firstname,
                                    'username': profile.username, 'url': profile.get_page_url()})

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

    def get_fields_size(self):
        l_username = 0
        l_email = 0
        l_firstname = 0
        l_lastname = 0
        l_patronymic = 0
        l_birth_date = 0
        l_avatar = 0
        l_password = 0

        if self.username:
            l_username = len(self.username)
        if self.email:
            l_email = len(self.email)
        if self.firstname:
            l_firstname = len(self.firstname)
        if self.lastname:
            l_lastname = len(self.lastname)
        if self.patronymic:
            l_patronymic = len(self.patronymic)
        if self.birth_date:
            l_birth_date = len(str(self.birth_date))
        if self.avatar:
            l_avatar = self.avatar.size
        if self.password:
            l_password = len(self.password)

        return {'username': l_username,
                'email': l_email,
                'firstname': l_firstname,
                'lastname': l_lastname,
                'patronymic': l_patronymic,
                'birth_date': l_birth_date,
                'avatar': l_avatar,
                'password': l_password,
                }

    def __str__(self):
        return self.username


class Relationship(models.Model):
    from_person = models.ForeignKey(User, related_name='from_people', on_delete=models.CASCADE)
    to_person = models.ForeignKey(User, related_name='to_people', on_delete=models.CASCADE)
    status = models.IntegerField(choices=RELATIONSHIP_STATUSES)

    class Meta:
        app_label = 'user_profile'
