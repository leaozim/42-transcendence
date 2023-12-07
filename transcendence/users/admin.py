# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User


from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User

# class UserAdmin(UserAdmin):
#     add_form = UserCreationForm
#     form = UserChangeForm
#     model = User
#     list_display = ['username', 'email', 'id_42', 'description', 'token_2f', 'is_2f_active', 'avatar', 'exp_game', 'wins', 'loses']    


admin.site.register(User)
