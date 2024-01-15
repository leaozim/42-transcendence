import jwt
from datetime import datetime, timedelta
from django.conf import settings
from srcs_user.models import User

class JWTVerificationFailed(Exception):
    pass
    
def generate_jwt_token(user_data):
    payload = {
        'id_42':  user_data['id'],
        'exp': datetime.utcnow() + timedelta(days=10),
        # 'exp': datetime.utcnow() + timedelta(seconds=20),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTVerificationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise JWTVerificationFailed("Invalid token")
    except Exception:
        raise JWTVerificationFailed("An unexpected error occurred during JWT verification")