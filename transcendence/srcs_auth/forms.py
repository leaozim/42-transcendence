from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from srcs_user.forms import AvatarField
from srcs_user.models import User


class UserCreationForm(UserCreationForm):
    # Optional; saved (resized) by SignUpView once the account exists.
    avatar = AvatarField()

    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class UserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = User
        fields = ('username', 'email')


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class TwoFactorCodeForm(forms.Form):
    token = forms.CharField(
        label=_("Security code"),
        max_length=7,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "pattern": "[0-9 ]*",
                "autofocus": True,
            }
        ),
    )

    def clean_token(self):
        # Authenticator apps display codes as "123 456"; accept them pasted that way.
        token = self.cleaned_data["token"].replace(" ", "")
        if len(token) != 6 or not token.isdigit():
            raise forms.ValidationError(_("Enter the 6-digit code from your app."))
        return token
