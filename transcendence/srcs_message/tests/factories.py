import factory
from srcs_message.models import Message
from srcs_user.tests.factories import UserFactory
from srcs_chat.tests.factories import ChatFactory

class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    chat = factory.SubFactory(ChatFactory)
    user = factory.SubFactory(UserFactory)
    content = factory.Faker('text', max_nb_chars=255)
