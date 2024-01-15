from functools import wraps
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed

def login_or_jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        jwt_token = request.COOKIES.get('jwt_token', None)
        if jwt_token:
            try:
                user = verify_jwt_token(jwt_token)
                if user:
                    request.user = user 
                    return view_func(request, *args, **kwargs)
            except JWTVerificationFailed as e:
                return HttpResponseRedirect(reverse('login'))
        
        return HttpResponseRedirect(reverse('login'))
    
    return _wrapped_view
