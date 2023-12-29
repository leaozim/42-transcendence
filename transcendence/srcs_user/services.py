from srcs_user.models import User
from django.http import Http404

def find_one(id):
    try:
        return User.objects.get(id=id)
    except User.DoesNotExist:
        raise Http404(f"User with ID {id} does not exist.")

def find_all():
    return User.objects.all()

def update(user_id, new_user):
    try:
        user = User.objects.get(id=user_id)
        user = new_user
        user.save()
    except User.DoesNotExist:
        raise Http404("User does not exist")

def delete_one(id):
    try:
        user = User.objects.get(id=id)
        user.delete()
    except User.DoesNotExist:
        raise Http404(f"User with ID {id} does not exist.")

def compute_mmr_points(user_id, points):
    try:
        user = User.objects.get(id=user_id)
        user.mmr += points
        user.save()
        return user
    except User.DoesNotExist:
        raise Http404(f"User with ID {user_id} does not exist.")
