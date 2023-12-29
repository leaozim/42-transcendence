import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from srcs_chat.models import Chat
import random
from srcs_user.tests.factories import UserFactory

class ChatFactory(factory.django.DjangoModelFactory):
    """ Creates fake Chats """

    class Meta:
        model = Chat
    
    @factory.post_generation
    def users_on_chat(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.users_on_chat.set(extracted)

    @factory.post_generation
    def create_users(self, create, extracted, **kwargs):
        if create:
            user1 = UserFactory()
            user2 = UserFactory()
            self.users_on_chat.set([user1, user2])
