from django.contrib.auth.backends import BaseBackend
from srcs_user.models import User
from srcs_auth.jwt_token import verify_jwt_token
import logging

class IntraAuthenticationBackend(BaseBackend):
    def authenticate(self, request, jwt_token, user_intra):
        if not isinstance(user_intra, dict):
            return None
        
        if jwt_token:
            user_data = verify_jwt_token(jwt_token)
            try:
                user = User.objects.get(id_42=user_data['id_42'])
            except User.DoesNotExist:
                user = User.objects.create_new_intra_user(user_intra)
                
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id_42=user_id)
        except User.DoesNotExist:
            return None
