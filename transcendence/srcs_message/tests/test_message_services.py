from django.test import TestCase
from srcs_message.models import Message
from srcs_chat.models import Chat
from srcs_user.tests.factories import UserFactory
from srcs_chat.tests.factories import ChatFactory
from srcs_message.tests.factories import MessageFactory


class TestMessage(TestCase):
    def setUp(self):
        self.chat = ChatFactory()
        self.user1, self.user2 = self.chat.usersChats.all()

    def tearDown(self):
        UserFactory.reset_sequence()
        ChatFactory.reset_sequence()
        MessageFactory.reset_sequence()

    def test_add_new_message_factory(self):
        message = MessageFactory(user=self.user1, chat=self.chat)
        MessageFactory(user=self.user2, chat=self.chat)
        MessageFactory(user=self.user1, chat=self.chat)

        messages = Message.objects.filter(chat=self.chat)
        
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(len(messages), 3)





    