import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from srcs_chat.models import Chat
import random
from srcs_user.tests.factories import UserFactory

class ChatFactory(factory.django.DjangoModelFactory):
    """ Creates fake Chats """

    class Meta:
        model = Chat

    id = factory.Sequence(lambda n: n + 1)
    blocked = False
    
    @factory.post_generation
    def usersChats(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.usersChats.set(extracted)

    @factory.post_generation
    def create_users(self, create, extracted, **kwargs):
        if create:
            user1 = UserFactory()
            user2 = UserFactory()
            self.usersChats.set([user1, user2])
