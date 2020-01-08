# Generated by Django 2.2.8 on 2020-01-08 04:14

import Net640.apps.images.models
import Net640.apps.user_posts.mixin
import Net640.mixin
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(Net640.mixin.LikesMixin, Net640.apps.user_posts.mixin.AsDictMessageMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('image', models.ImageField(upload_to=Net640.apps.images.models.user_directory_path)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(Net640.mixin.LikesMixin, Net640.apps.user_posts.mixin.AsDictMessageMixin, models.Model),
        ),
    ]