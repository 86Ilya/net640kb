# Generated by Django 2.2.10 on 2020-06-17 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_user_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar_size',
            field=models.IntegerField(default=0),
        ),
    ]
