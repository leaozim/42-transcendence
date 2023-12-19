from .models import User

"""
find all

find one

update

delete one

computeVictory

computeLoss

computeExperience
"""
def find_one(id):
    return User.objects.get(id = id)

def find_all():
    return User.objects.get()

def update(id, User):
    pass

def delete_one(id):
    pass

def computeVictory(id):
    pass

def computeLoss(id):
    pass

def computeExperience(id, exp):
    pass
