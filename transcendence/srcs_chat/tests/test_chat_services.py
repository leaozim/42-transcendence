from django.test import TestCase
from srcs_chat import services
from srcs_chat.models import Chat
from srcs_message.models import Message
from srcs_user.tests.factories import UserFactory
from srcs_chat.tests.factories import ChatFactory
from django.utils import timezone

# Create your tests here.
# @transaction.atomic
class ChatTests(TestCase):

    def setUp(self):
        self.chat = ChatFactory()

    def tearDown(self):
        ChatFactory.reset_sequence()
        UserFactory.reset_sequence()

    def test_chat_creation_factory(self):
        self.assertEqual(self.chat.usersChats.count(), 2)
        self.assertEqual(self.chat.blocked, False)
        self.assertEqual(self.chat.id, 1)
