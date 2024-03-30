import os
from django.core.management.base import BaseCommand
from srcs_user.models import User
from srcs_chat.services import open_chat
from srcs_message.services import add_message

class Command(BaseCommand):
    help = "Cria um superusuário padrão automaticamente"

    def handle(self, *args, **options):
        username = os.getenv("POSTGRES_USER") + " (BOT)"
        email = ""
        password = os.getenv("POSTGRES_PASSWORD")
        try:
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superusuário "{user}" já existe. Nenhum novo superusuário foi criado.'
                )
            )
        except User.DoesNotExist:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" criado com sucesso!'))
        user = User.objects.create_superuser('cavalao', '', password)
        chat = open_chat(1, user.id)
        add_message(chat.id, "Olá humano!", 1)
        user = User.objects.create_superuser('cavalord', '' , password)
        chat = open_chat(1, user.id)
        add_message(chat.id, "Olá humano!", 1)
