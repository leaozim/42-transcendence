# Generated by Django 4.2.8 on 2023-12-07 20:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ownerId', models.IntegerField(db_column='owner_id', unique=True)),
                ('isPublic', models.IntegerField(db_column='is_public')),
                ('password', models.BinaryField(null=True)),
                ('banneds', models.ManyToManyField(blank=True, related_name='chats_banned', to=settings.AUTH_USER_MODEL)),
                ('owner', models.OneToOneField(db_column='owner', on_delete=django.db.models.deletion.CASCADE, related_name='chats_owned', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
