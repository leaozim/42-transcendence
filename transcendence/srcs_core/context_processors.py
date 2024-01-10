from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed

def custom_context_processor(request):
    if request.user.is_authenticated:
        return {'current_user': request.user}
    jwt_token = request.COOKIES.get('jwt_token', None)
    if jwt_token:
        try:
            user = verify_jwt_token(jwt_token)
            if user:
                return {'current_user': user}
        except JWTVerificationFailed as e:
                return {}
    return {}