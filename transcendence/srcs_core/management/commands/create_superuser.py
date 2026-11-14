import os

from django.core.management.base import BaseCommand
from srcs_user.models import User
from srcs_chat.services import open_chat
from srcs_message.services import add_message


class Command(BaseCommand):
    help = "Cria um superusuário padrão automaticamente"

    def handle(self, *args, **options):
        # BOT_USERNAME/BOT_PASSWORD are preferred; POSTGRES_USER/POSTGRES_PASSWORD are
        # kept as fallbacks so existing .env files keep producing the same bot user.
        base_name = os.getenv("BOT_USERNAME") or os.getenv("POSTGRES_USER") or "pong"
        username = base_name + " (BOT)"
        email = ""
        # With no password configured the bot gets an unusable password (no login).
        password = os.getenv("BOT_PASSWORD") or os.getenv("POSTGRES_PASSWORD") or None
        try:
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superusuário "{user}" já existe. Nenhum novo superusuário foi criado.'
                )
            )
        except User.DoesNotExist:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(f'Superusuário "{username}" criado com sucesso!')
            )