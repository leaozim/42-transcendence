from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.templatetags.static import static
from srcs_user.managers import IntraUserOAuth2Manager
from django.db.models.signals import post_save
from django.dispatch import receiver


# Avatar shown until the user uploads one. Served locally (was a Cloudinary URL).
DEFAULT_AVATAR = "images/sloth.jpg"


def default_avatar():
    return static(DEFAULT_AVATAR)


class User(AbstractUser, PermissionsMixin):
    objects = IntraUserOAuth2Manager()
    id_42 = models.IntegerField(unique=True, null=True, blank=True, db_column="id_42")
    description = models.TextField(blank=True)
    token_2F = models.CharField(max_length=255, blank=True, db_column="token_2f")
    is_2f_active = models.BooleanField(default=False, db_column="is_2f_active")
    # URL of the avatar: an uploaded file under MEDIA_URL, a 42 intra picture,
    # or the local default.
    avatar = models.CharField(max_length=255, blank=True, default=default_avatar)
    mmr = models.FloatField(default=0)
    tournament_alias = models.CharField(max_length=255, blank=True)
    
    @property
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    class Meta:
        db_table = "user"


class BlockedUser(models.Model):
    blocked_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocked_by", default=None
    )
    blocked_user_id = models.IntegerField(
        db_column="blocked_user_id", verbose_name="blocked_user_id", default=None
    )

@receiver(post_save, sender=User)
def schedule_tournament_close(sender, instance, created, **kwargs):
    if created:
        instance.tournament_alias = instance.username
        instance.save()
