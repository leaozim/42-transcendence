from functools import wraps
from django.shortcuts import redirect

def two_factor_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_2f_active:
            if not request.session.get('is_two_factor_authenticated', False):
                return redirect('/')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
