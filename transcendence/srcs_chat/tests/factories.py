import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from srcs_chat.models import Chat, Message
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
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_chats')
    messages = models.ManyToManyField(
        User, 
        through="Message",
        through_fields=("chat", "user"), blank=True)
    usersChats =  models.ManyToManyField(User, related_name='users_chats', blank=True, db_column='users_chats')
    """

class MessageFactory(factory.django.DjangoModelFactory):
    """ Creates fake Chats """

    class Meta:
        model = Chat

    id = factory.Sequence(lambda n: n + 1)

    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, db_column='content')
    dateTime = models.DateTimeField(db_column='date_time')
    """