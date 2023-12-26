
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from srcs_users.forms import UserCreationForm, UserChangeForm
from srcs_users.models import User

admin.site.register(User)

