from django.test import TestCase
from srcs_chat import services
from srcs_chat.models import Chat
from srcs_message.models import Message
from srcs_user.tests.factories import UserFactory
from django.utils import timezone

# Create your tests here.
# @transaction.atomic
class ChatTests(TestCase):

    def tearDown(self):
        UserFactory.reset_sequence()
