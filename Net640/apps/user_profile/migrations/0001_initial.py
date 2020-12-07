# Generated by Django 2.2.8 on 2020-01-08 04:14

import Net640.apps.images.models
import Net640.apps.user_profile.models
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=120, null=True, unique=True, verbose_name='username')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('firstname', models.CharField(max_length=120, null=True, verbose_name='first name')),
                ('lastname', models.CharField(blank=True, max_length=120, null=True, verbose_name='last name')),
                ('patronymic', models.CharField(blank=True, max_length=120, null=True, verbose_name='patronymic')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='birth date')),
                ('is_active', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('avatar', models.ImageField(default=None, upload_to=Net640.apps.images.models.user_avatar_path)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model, Net640.apps.user_profile.mixin.GetSizeMixin, Net640.apps.user_profile.mixin.SendMessagesToFrontEndMixin),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserResetPassword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=120, verbose_name='confirmation code')),
                ('sent', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserConfirmationCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=120, verbose_name='confirmation code')),
                ('sent', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Waiting'), (2, 'Friends'), (3, 'Blocked')])),
                ('from_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_people', to=settings.AUTH_USER_MODEL)),
                ('to_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_people', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='relationships',
            field=models.ManyToManyField(related_name='_user_relationships_+', through='user_profile.Relationship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
