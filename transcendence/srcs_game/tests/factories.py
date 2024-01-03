import factory
from srcs_user.tests.factories import UserFactory
from srcs_game.models import Game

class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    leftPlayer = factory.SubFactory(UserFactory)
    rightPlayer = factory.SubFactory(UserFactory)
    leftPlayerScore = 0
    rightPlayerScore = 0