import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from srcs_chat.models import Chat
import random
from srcs_user.tests.factories import UserFactory

    # Example:
    # username = factory.Faker('name')
    # id42 = factory.LazyAttribute(lambda _: random.randrange(1000, 9999))
    # description = factory.Faker('sentence', nb_words=10)
    # is2fActive = FuzzyChoice(choices=[True, False])
    # expGame = factory.LazyAttribute(lambda _:random.randrange(0, 50))
    # wins = factory.LazyAttribute(lambda _:random.randrange(0, 50))
    # loss = factory.LazyAttribute(lambda _:random.randrange(0, 50))

class ChatFactory(factory.django.DjangoModelFactory):
    """ Creates fake Chats """

    class Meta:
        model = Chat

    id = factory.Sequence(lambda n: n + 1)
