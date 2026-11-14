from functools import wraps
from django.shortcuts import redirect

def two_factor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        
        if request.user.is_authenticated and request.user.is_2f_active:
            # Sessions created by the password + code login are verified by
            # django_otp; the cookie is set by the in-page code prompt.
            is_verified = getattr(request.user, 'is_verified', lambda: False)()
            if not is_verified and not request.COOKIES.get('two_factor', None):
                return redirect('srcs_auth:validate_token_2f')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
