from django.test import TestCase
from srcs_message.models import Message
from srcs_message import services as messageServices
from srcs_chat.models import Chat
from srcs_chat import services as chatServices
from srcs_user.tests.factories import UserFactory
from srcs_chat.tests.factories import ChatFactory
from srcs_message.tests.factories import MessageFactory


class TestMessage(TestCase):
    def setUp(self):
        self.chat = ChatFactory()
        self.user1, self.user2 = self.chat.users_on_chat.all()

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

    def test_add_message_to_an_unblocked_chat_should_succeed(self):
        messages = Message.objects.filter(chat=self.chat)
        self.assertEqual(len(messages), 0) # Just to garantee that it starts with 0 messages
        messageServices.add_message(chat_id=self.chat.id, content='cavalinho', user=self.user1.id)

        messages = Message.objects.filter(chat=self.chat)
        self.assertEqual(len(messages), 1)
    
    def test_add_message_to_block_chat_should_fail(self):
        messages = Message.objects.filter(chat=self.chat)
        self.assertEqual(len(messages), 0)
        chatServices.block_chat(self.chat.id)

        messageServices.add_message(chat_id=self.chat.id, content='cavalinho', user=self.user1.id) # Choose to handle return or raise exception

        messages = Message.objects.filter(chat=self.chat)
        self.assertEqual(len(messages), 0) # if raise exception, use assertRaises instead

    def test_add_message_with_more_than_500_characteres_should_fail(self):
        messages = Message.objects.filter(chat=self.chat)
        self.assertEqual(len(messages), 0)

        messageServices.add_message(chat_id=self.chat.id, content=('créu' * 500), user=self.user1.id)

        self.assertEqual(len(messages), 0)

    def test_add_message_with_less_than_1_charactere_should_fail(self):
        messages = Message.objects.filter(chat=self.chat)
        self.assertEqual(len(messages), 0)

        messageServices.add_message(chat_id=self.chat.id, content=(''), user=self.user1.id)

        self.assertEqual(len(messages), 0)



        





    