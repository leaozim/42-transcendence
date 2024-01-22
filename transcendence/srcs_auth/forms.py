from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from srcs_user.models import User


class UserCreationForm(UserCreationForm):

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
