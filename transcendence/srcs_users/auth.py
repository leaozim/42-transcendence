from django.contrib.auth.backends import BaseBackend
from .models import User
# from django.contrib.auth.models import User

class IntraAuthenticationBackend(BaseBackend):
  def authenticate(self, request, user) -> User:
    find_user = User.objects.filter(id=user['id'])
    if len(find_user) == 0:
      print('User was not found. Saving...')
      new_user = User.objects.create_new_intra_user(user)
      print(new_user)
      return new_user
    print('User was found. Returning...')
    return find_user

  def get_user(self, user_id):
    try:
      return User.objects.get(pk=user_id)
    except User.DoesNotExist:
      return None