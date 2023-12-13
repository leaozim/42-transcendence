import jwt
from datetime import datetime, timedelta
from django.conf import settings
from .models import User

def generate_jwt_token(user_data):
    payload = {
        'user_id':  user_data['id'],
        'exp': datetime.utcnow() + timedelta(days=1),  # Expira em 1 dia
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print( "payload",payload)
        user_id = payload['user_id']
        return User.objects.get(id42=user_id)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except User.DoesNotExist:
        return None