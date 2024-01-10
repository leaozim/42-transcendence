import jwt
from datetime import datetime, timedelta
from django.conf import settings
from srcs_user.models import User

class JWTVerificationFailed(Exception):
    pass
    
def generate_jwt_token(user_data):
    payload = {
        'id_42':  user_data['id'],
        'exp': datetime.utcnow() + timedelta(days=1),
        # 'exp': datetime.utcnow() + timedelta(minutes=1),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        id_42 = payload['id_42']
        user = User.objects.get(id42=id_42)
        return user
    except jwt.ExpiredSignatureError:
        raise JWTVerificationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise JWTVerificationFailed("Invalid token")
    except User.DoesNotExist:
        raise JWTVerificationFailed("User does not exist")
    except Exception:
        raise JWTVerificationFailed("An unexpected error occurred during JWT verification")