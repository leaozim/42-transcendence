import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from srcs_user.models import User
import random

class UserFactory(factory.django.DjangoModelFactory):
    """ Creates fake Users """

    class Meta:
        model = User
    
    username = factory.Faker('name')
    id_42 = factory.LazyAttribute(lambda _: random.randrange(1000, 9999))
    description = factory.Faker('sentence', nb_words=10)
    is_2f_active = FuzzyChoice(choices=[True, False])
    mmr = factory.LazyAttribute(lambda _:random.randrange(0, 50))
    avatar = 'https://res.cloudinary.com/dw9xon1xs/image/upload/v1706288572/arya2_lr9qcd.png'


"""
    token2F = models.CharField(max_length=255, blank=True, db_column='token_2f')
    blockedUsers = models.ManyToManyField('self', symmetrical=False, related_name='blocking_users', blank=True, db_column='blocked_users')
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following_users', blank=True)
    friendships = models.ManyToManyField('self', symmetrical=False, related_name='friend_users', blank=True)
"""    