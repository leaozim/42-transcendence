# Generated by Django 4.2.8 on 2023-12-26 18:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('srcs_chat', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='admins',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='banneds',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='isPublic',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='muteds',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='password',
        ),
        migrations.RemoveField(
            model_name='message',
            name='dateTime',
        ),
        migrations.AddField(
            model_name='chat',
            name='blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='chat',
            name='messages',
            field=models.ManyToManyField(blank=True, related_name='chats', through='srcs_chat.Message', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterModelTable(
            name='chat',
            table='chat',
        ),
    ]
