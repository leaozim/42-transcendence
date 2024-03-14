from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from srcs_user.models import User

from .models import BlockedUser


class BlockForm(forms.Form):

    @staticmethod
    def blocked_user_name_validator(value):
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise ValidationError(
                _("%(value) isn't a valid user"), params={"value": value}
            )

    blockedUserName = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        validators=[blocked_user_name_validator],
    )

    class Meta:
        model = BlockedUser
