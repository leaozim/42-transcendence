from django.test import TestCase
from srcs_chat import services
from srcs_chat.models import Chat, Message
from srcs_users.tests.factories import UserFactory
from django.utils import timezone

# Create your tests here.
# @transaction.atomic
class ChatTests(TestCase):
    def tearDown(self):
        UserFactory.reset_sequence()

    def setUp(self):
        self.owner = UserFactory()
        self.other_user = UserFactory()
        self.chat = Chat.objects.create(owner=self.owner)
        self.chat.usersChats.add(self.other_user)

    def test_chat_creation(self):
        self.assertEqual(self.owner, self.chat.owner)
        self.assertIn(self.other_user, self.chat.usersChats.all())

    def test_chat_with_message(self):
        time_now = timezone.now()
        message = Message.objects.create(chat=self.chat, user=self.owner, content='cavalinho', dateTime=time_now)
        self.chat.refresh_from_db()
        message.refresh_from_db()
        
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.user, self.owner)
        self.assertEqual(message.content, 'cavalinho')
        self.assertIn(message, self.chat.messages.all())


        

"""
find all public

find my chats

find one

update

delete one

add admin

remove admin

change password

lock chat

unlock chat

change owner

ban user

mute user

unmute user
"""