from django.contrib.auth import models

class IntraUserOAuth2Manager(models.UserManager):
    def create_new_intra_user(self, user):
        existing_user = self.filter(id42=user['id']).first()
        if existing_user:
            return existing_user
        new_user = self.create(
            id42=user['id'],
            avatar=user['url'],
            email=user['email'],
            username=user['login'],
        )
        return new_user
        
    def create_superuser(self, email, username, password=None, **extra_fields):
        existing_user = self.filter(username=username).first()
        if existing_user:
            return existing_user
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)