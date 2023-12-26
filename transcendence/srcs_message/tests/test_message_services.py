from django.test import TestCase
from srcs_message.models import Message
from srcs_chat.models import Chat
from srcs_user.tests.factories import UserFactory


class TestMessage(TestCase):
    def tearDown(self):
        UserFactory.reset_sequence()

    def test_add_new_message(self):
        user1 = UserFactory()
        user2 = UserFactory()
        chat = Chat.objects.create()
        chat.usersChats.add(user1)
        chat.usersChats.add(user2)
        message = Message.objects.create(chat=chat, user=user1, content='cavalinho')
        Message.objects.create(chat=chat, user=user2, content='ao vento')
        Message.objects.create(chat=chat, user=user1, content='tomando chuva')

        messages = Message.objects.filter(chat=chat)
        
        self.assertEqual(message.chat, chat)
        self.assertEqual(len(messages), 3)





    