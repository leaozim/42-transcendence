from django.contrib.auth import models

class IntraUserOAuth2Manager(models.UserManager):
    def create_new_intra_user(self, user):
        if not all([user.get('id'), user.get('login'), user.get('email')]):
            return None
        
        existing_user = self.filter(id_42=user['id']).first()
        if existing_user:
            return existing_user
        
        avatar_link = user['image'].get('link')
        if avatar_link is None:
            avatar_link = 'https://res.cloudinary.com/dw9xon1xs/image/upload/v1699535128/nico_nk9vdi.jpg' 
            
        new_user = self.create(
            id_42=user['id'],
            avatar=avatar_link,
            email=user['email'],
            username=user['login'],
        )
        return new_user
        
    def create_superuser(self, username, email, password=None, **extra_fields):
        existing_user = self.filter(username=username).first()
        if existing_user:
            existing_user.is_staff = True
            existing_user.is_superuser = True
            existing_user.save()
            return existing_user
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)