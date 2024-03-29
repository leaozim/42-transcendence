from django.test import TransactionTestCase
from srcs_chat import services as chatServices
from srcs_chat.models import Chat
from srcs_message.models import Message
from srcs_user.tests.factories import UserFactory
from srcs_chat.tests.factories import ChatFactory
from django.http import Http404

# Create your tests here.
SETUP_CHAT_ID = 1

# @transaction.atomic
class ChatTests(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        self.chat = ChatFactory()
        self.user1, self.user2 = self.chat.users_on_chat.all()

    def tearDown(self):
        ChatFactory.reset_sequence()
        UserFactory.reset_sequence()
        

    def test_chat_creation_factory(self):
        self.assertEqual(self.chat.users_on_chat.count(), 2)
        self.assertEqual(self.chat.blocked, False)
        self.assertEqual(self.chat.id, 1)

    def test_block_chat(self):
        self.chat = chatServices.block_chat(SETUP_CHAT_ID, 1)

        self.assertTrue(Chat.objects.get(id=SETUP_CHAT_ID).id)

    def test_unblock_chat(self):
        self.assertFalse(self.chat.blocked)
        self.chat = chatServices.block_chat(SETUP_CHAT_ID, 1)

        self.assertTrue(self.chat.blocked)
        self.chat = chatServices.unblock_chat(SETUP_CHAT_ID, 1)

        self.assertFalse(self.chat.blocked)

    def test_block_and_unblock_chat_twice_in_a_row_should_not_affect_it(self):
        self.chat = chatServices.block_chat(SETUP_CHAT_ID, 1)
        self.chat = chatServices.block_chat(SETUP_CHAT_ID, 1)
        
        self.assertTrue(self.chat.blocked)

        self.chat = chatServices.unblock_chat(SETUP_CHAT_ID, 1)
        self.chat = chatServices.unblock_chat(SETUP_CHAT_ID, 1)

        self.assertFalse(self.chat.blocked)

    def test_open_chat(self):
        start_chat_count = Chat.objects.all().count()
        UserFactory()

        self.chat = chatServices.open_chat(2, 3)
        result_chat_count = Chat.objects.all().count()

        self.assertEqual(result_chat_count, start_chat_count + 1)

        self.chat = chatServices.open_chat(1, 3)
        result_chat_count = Chat.objects.all().count()

        self.assertEqual(result_chat_count, start_chat_count + 2)

    def test_show_open_chats_should_show_all_chats_that_user_are_in(self):
        # users 1 and 2 already start with an open chat because the setUp factory
        for _ in range(5):
            UserFactory()
        
        result = chatServices.find_open_chats(1)

        self.assertEqual(len(result), 1)

        self.chat = chatServices.open_chat(1, 3)
        result = chatServices.find_open_chats(1)

        self.assertEqual(len(result), 2)

        chatServices.open_chat(1, 4)
        chatServices.open_chat(2, 4)
        chatServices.open_chat(2, 3)
        chatServices.open_chat(3, 4)
        result = chatServices.find_open_chats(1)

        self.assertEqual(len(result), 3)

        result = chatServices.find_open_chats(4)

        self.assertEqual(len(result), 3)

    def test_block_chat_when_user_doesnt_exist_should_raise_Http404(self):
        user_id = 999999999
        with self.assertRaises(Http404) as context:
            chatServices.block_chat(1, user_id)
        
        message = str(context.exception)
        self.assertEqual(message, f"User with ID {user_id} does not exist.")

    def test_block_chat_when_chat_doesnt_exist_should_raise_Http404(self):
        chat_id = 999999999
        with self.assertRaises(Http404) as context:
            chatServices.block_chat(chat_id, 1)
        
        message = str(context.exception)
        self.assertEqual(message, f"Chat with ID {chat_id} does not exist.")

    def test_unblock_chat_can_only_be_performed_by_the_user_who_bocked_it_first(self):
        chatServices.block_chat(SETUP_CHAT_ID, 1)

        chat = chatServices.unblock_chat(SETUP_CHAT_ID, 2)

        self.assertTrue(chat.blocked)

    def test_block_chat_can_only_be_performed_by_players_in_chat(self):
        UserFactory()
        UserFactory()
        chat = chatServices.block_chat(SETUP_CHAT_ID, 3)

        self.assertFalse(chat.blocked)

    def test_unblock_chat_can_only_be_performed_by_players_in_chat(self):
        UserFactory()
        UserFactory()
        chatServices.block_chat(SETUP_CHAT_ID, 1)
        chat = chatServices.unblock_chat(SETUP_CHAT_ID, 3)

        self.assertTrue(chat.blocked)
