"""Who is behind a WebSocket connection."""

from http.cookies import CookieError, SimpleCookie

from channels.db import database_sync_to_async
from srcs_auth.jwt_token import JWTVerificationFailed, verify_jwt_token
from srcs_user.models import User


def _cookies(scope):
    for name, value in scope.get("headers", []):
        if name == b"cookie":
            cookie = SimpleCookie()
            try:
                cookie.load(value.decode("latin-1"))
            except CookieError:
                return {}
            return {key: morsel.value for key, morsel in cookie.items()}
    return {}


@database_sync_to_async
def _user_id_from_jwt(token):
    try:
        payload = verify_jwt_token(token)
    except JWTVerificationFailed:
        return None
    return User.objects.filter(id_42=payload.get("id_42")).values_list("id", flat=True).first()


async def resolve_user_id(scope):
    """
    Id of the logged-in user, decided like the HTTP middleware does: a valid
    jwt_token cookie (42 login) wins, otherwise the session user. None for
    anonymous visitors.
    """
    token = _cookies(scope).get("jwt_token")
    if token:
        user_id = await _user_id_from_jwt(token)
        if user_id:
            return user_id
    user = scope.get("user")
    if user is not None and user.is_authenticated:
        return user.id
    return None
