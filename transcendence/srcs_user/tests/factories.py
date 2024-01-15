import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from srcs_user.models import User
import random

class UserFactory(factory.django.DjangoModelFactory):
    """ Creates fake Users """

    class Meta:
        model = User
    
    username = factory.Faker('name')
    id42 = factory.LazyAttribute(lambda _: random.randrange(1000, 9999))
    description = factory.Faker('sentence', nb_words=10)
    is2fActive = FuzzyChoice(choices=[True, False])
    mmr = factory.LazyAttribute(lambda _:random.randrange(0, 50))


"""
    token2F = models.CharField(max_length=255, blank=True, db_column='token_2f')
    avatar = models.CharField(max_length=255, blank=True)
    blockedUsers = models.ManyToManyField('self', symmetrical=False, related_name='blocking_users', blank=True, db_column='blocked_users')
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following_users', blank=True)
    friendships = models.ManyToManyField('self', symmetrical=False, related_name='friend_users', blank=True)
"""    