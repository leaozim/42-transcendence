# Generated by Django 4.2.8 on 2023-12-29 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blocked', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'chat',
            },
        ),
    ]
