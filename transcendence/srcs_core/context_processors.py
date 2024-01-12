from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed

def custom_context_processor(request):
    if request.user.is_authenticated:
        return {'current_user': request.user}
    return {}