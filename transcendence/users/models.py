from django.db import models

class User(models.Model):
    id_42 = models.IntegerField(unique=True)
    user_name = models.CharField(max_length=50, unique=True, db_column='user_name')
    email = models.EmailField(unique=True)
    description = models.CharField(max_length=300, blank=True)
    password = models.BinaryField()
    token_2f = models.CharField(max_length=255, blank=True)
    is_2f_active = models.BooleanField(default=False, db_column='is_2f_active')
    avatar = models.CharField(max_length=255, blank=True)
    exp_game = models.FloatField(default=0)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)

    class Meta:
        db_table = 'user'
