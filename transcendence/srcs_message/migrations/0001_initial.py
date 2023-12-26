# Generated by Django 4.2.8 on 2023-12-26 18:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('srcs_chat', '0003_remove_chat_messages_delete_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(db_column='content', max_length=500)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='srcs_chat.chat')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='message', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'message',
            },
        ),
    ]
