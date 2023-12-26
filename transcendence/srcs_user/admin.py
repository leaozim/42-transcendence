
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from srcs_user.forms import UserCreationForm, UserChangeForm
from srcs_user.models import User

admin.site.register(User)

