from django.contrib.auth import models

class IntraUserOAuth2Manager(models.UserManager):
  def create_new_intra_user(self, user):
    print("inside intra user menager")
    existing_user = self.filter(id42=user['id']).first()
    if existing_user:
        print("User already exists")
        return existing_user
    new_user = self.create(
        id42=user['id'],
        avatar=user['url'],
        email=user['email'],
        username=user['login'],
    )
    print("New user created")
    return new_user