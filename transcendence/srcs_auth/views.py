import math
import os
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET
from django.views.generic.edit import CreateView
from srcs_auth.auth import IntraAuthenticationBackend
from srcs_auth.decorators import two_factor_required
from srcs_auth.forms import TwoFactorCodeForm, UserCreationForm, UserLoginForm
from srcs_auth.jwt_token import (JWTVerificationFailed, generate_jwt_token,
                                 verify_jwt_token)
from srcs_auth.services import (
    AUTHENTICATOR_APPS,
    DEFAULT_AUTHENTICATOR_APP,
    TOTPService,
    exchange_code,
)
from srcs_user.models import User, default_avatar
from srcs_user.services import save_avatar


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("srcs_home:home")
    template_name = "account/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["default_avatar_url"] = default_avatar()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get("avatar"):
            save_avatar(self.object, form.cleaned_data["avatar"])
        messages.success(self.request, _("Account created. You can log in now."))
        return response


# --- Username/password login with an optional two-factor step ----------------
#
# Step 1 (PasswordLoginView) checks the password. Users without two-factor
# authentication are logged in right away. For users with a confirmed TOTP
# device nothing is logged in yet: the user id is parked server-side in the
# session and step 2 (LoginTwoFactorView) only calls login() once a valid code
# from the authenticator app is entered.

PENDING_2FA_USER_KEY = "pending_2fa_user_id"
PENDING_2FA_BACKEND_KEY = "pending_2fa_backend"
PENDING_2FA_NEXT_KEY = "pending_2fa_next"
PENDING_2FA_EXPIRES_KEY = "pending_2fa_expires"
# Seconds the user has to enter the code after typing the correct password.
PENDING_2FA_TIMEOUT = 300


def _safe_next_url(request, url):
    if url and url_has_allowed_host_and_scheme(
        url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return url
    return reverse("srcs_home:home")


def render_login_page(request, form=None):
    """Render the landing page, which holds the login form."""
    if form is None:
        form = UserLoginForm(request)
    next_url = request.POST.get("next") or request.GET.get("next", "")
    return render(request, "index.html", {"form": form, "next": next_url})


def _clear_pending_login(request):
    for key in (
        PENDING_2FA_USER_KEY,
        PENDING_2FA_BACKEND_KEY,
        PENDING_2FA_NEXT_KEY,
        PENDING_2FA_EXPIRES_KEY,
    ):
        request.session.pop(key, None)


def _complete_login(request, user, backend, next_url, device=None):
    if device is not None:
        # django_otp marks the session as OTP-verified when login() sees this.
        user.otp_device = device
    login(request, user, backend)
    response = redirect(_safe_next_url(request, next_url))
    # A JWT left over from a 42 login would override this session's user.
    response.delete_cookie("jwt_token")
    return response


@method_decorator(never_cache, name="dispatch")
class PasswordLoginView(View):
    def get(self, request: HttpRequest):
        if request.user.is_authenticated:
            return redirect(_safe_next_url(request, request.GET.get("next")))
        return render_login_page(request)

    @method_decorator(csrf_protect)
    def post(self, request: HttpRequest):
        form = UserLoginForm(request, data=request.POST)
        if not form.is_valid():
            return render_login_page(request, form)

        user = form.get_user()
        next_url = request.POST.get("next", "")
        device = TOTPService().get_user_totp_device(user, confirmed=True)
        if device is None:
            return _complete_login(request, user, user.backend, next_url)

        _clear_pending_login(request)
        request.session[PENDING_2FA_USER_KEY] = user.pk
        request.session[PENDING_2FA_BACKEND_KEY] = user.backend
        request.session[PENDING_2FA_NEXT_KEY] = next_url
        request.session[PENDING_2FA_EXPIRES_KEY] = time.time() + PENDING_2FA_TIMEOUT
        return redirect("srcs_auth:login-2fa")


@method_decorator(never_cache, name="dispatch")
class LoginTwoFactorView(View):
    template_name = "registration/login_2fa.html"

    def _get_pending(self, request):
        """Return (user, device) for the login awaiting a code, or (None, None)."""
        user_id = request.session.get(PENDING_2FA_USER_KEY)
        expires = request.session.get(PENDING_2FA_EXPIRES_KEY, 0)
        if user_id is None or time.time() > expires:
            _clear_pending_login(request)
            return None, None
        user = User.objects.filter(pk=user_id).first()
        device = TOTPService().get_user_totp_device(user, confirmed=True) if user else None
        if device is None:
            _clear_pending_login(request)
            return None, None
        return user, device

    def _expired(self, request):
        messages.error(request, _("Your login attempt expired. Please log in again."))
        return redirect("srcs_home:home")

    def _render(self, request, form, device):
        context = {"form": form, "app_name": device.name or _("your authenticator app")}
        return render(request, self.template_name, context)

    def get(self, request: HttpRequest):
        user, device = self._get_pending(request)
        if device is None:
            return self._expired(request)
        return self._render(request, TwoFactorCodeForm(), device)

    @method_decorator(csrf_protect)
    def post(self, request: HttpRequest):
        user, device = self._get_pending(request)
        if device is None:
            return self._expired(request)

        form = TwoFactorCodeForm(request.POST)
        if form.is_valid():
            # django_otp throttles a device after failed attempts (exponential back-off).
            allowed, info = device.verify_is_allowed()
            if not allowed:
                locked_until = (info or {}).get("locked_until")
                seconds = 1
                if locked_until:
                    seconds = max(1, math.ceil((locked_until - timezone.now()).total_seconds()))
                form.add_error(
                    "token",
                    ngettext(
                        "Too many failed attempts. Try again in %(seconds)s second.",
                        "Too many failed attempts. Try again in %(seconds)s seconds.",
                        seconds,
                    )
                    % {"seconds": seconds},
                )
            elif device.verify_token(form.cleaned_data["token"]):
                backend = request.session[PENDING_2FA_BACKEND_KEY]
                next_url = request.session.get(PENDING_2FA_NEXT_KEY, "")
                _clear_pending_login(request)
                return _complete_login(request, user, backend, next_url, device)
            elif TOTPService().is_reused_token(device, form.cleaned_data["token"]):
                form.add_error(
                    "token",
                    _("This code was already used. Wait for the next code in %(app)s.")
                    % {"app": device.name or _("your authenticator app")},
                )
            else:
                form.add_error("token", _("Invalid code. Please try again."))
        return self._render(request, form, device)


@two_factor_required
def get_authenticated_user(request):
    if request.user.is_authenticated:
        return redirect("srcs_home:home")

    return JsonResponse({"error": _("User not authenticated")}, status=401)


def intra_login(request: HttpRequest):
    return redirect(os.environ.get("AUTH_URL_INTRA"))


def intra_login_redirect(request: HttpRequest):
    code = request.GET.get("code")
    user_intra = exchange_code(code)
    jwt_token = generate_jwt_token(user_intra)
    user = IntraAuthenticationBackend().authenticate(
        request, jwt_token=jwt_token, user_intra=user_intra
    )

    if user:
        login(request, user, "srcs_auth.auth.IntraAuthenticationBackend")

    if user.is_2f_active:
        response = redirect("srcs_auth:validate_token_2f")
    else:
        response = redirect("srcs_auth:get_authenticated_user")

    response.set_cookie("jwt_token", jwt_token, httponly=True, samesite="Lax")
    return response


def logout_user(request):
    response = redirect("srcs_home:home")
    response.delete_cookie("jwt_token")
    response.delete_cookie("two_factor")
    request.session.flush()
    logout(request)
    return response


def refresh_token(request):
    jwt_token = request.COOKIES.get("jwt_token")

    if jwt_token:
        try:
            user_data = verify_jwt_token(jwt_token)
            new_jwt_token = generate_jwt_token(user_data)
            response = JsonResponse({"jwt_token": new_jwt_token})
            response.set_cookie(
                "jwt_token", new_jwt_token, httponly=True, samesite="Lax"
            )
            return response
        except JWTVerificationFailed:
            pass

    return JsonResponse({"error": _("Could not refresh the token.")}, status=400)


class TOTPCreateView(LoginRequiredMixin, View):
    def _create_qrcode(self, request: HttpRequest):
        user = request.user
        totp_service = TOTPService()

        app = request.GET.get("app", DEFAULT_AUTHENTICATOR_APP)
        if app not in AUTHENTICATOR_APPS:
            return JsonResponse({"error": "Unknown authenticator app"}, status=400)

        qr_code, totp_code = totp_service.create_totp_code(user, app)
        return JsonResponse(
            {
                "qrcode": qr_code,
                "totp_code": totp_code,
                "app": app,
                "app_name": AUTHENTICATOR_APPS[app]["name"],
            },
            status=200,
        )

    def get(self, request: HttpRequest, *args, **kwargs):
        return self._create_qrcode(request)


class TOTPVerifyView(LoginRequiredMixin, View):
    @staticmethod
    @require_GET
    def get(request: HttpRequest, *args, **kwargs):
        if request.user.is_2f_active:
            return JsonResponse({}, status=200)
        return JsonResponse({}, status=204)

    @method_decorator(csrf_protect)
    def post(self, request: HttpRequest, token: str) -> JsonResponse:
        user = request.user
        totp_service = TOTPService()

        if totp_service.verify_totp_token(user, token):
            response = JsonResponse({"success": True}, status=201)
            response.set_cookie(
                "two_factor",
                True,
                max_age=3600,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=True,
                samesite="Lax",
            )
            return response

        return JsonResponse({"success": False}, status=400)


class TOTPDeleteView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        totp_service = TOTPService()

        if totp_service.delete_totp_devices(user):
            return JsonResponse(
                {"success": "TOTP devices deleted successfully"}, status=200
            )


@require_GET
@login_required
def validate_token_2f(request):
    return render(request=request, template_name="registration/verifyAtLogin.html")


def get_authenticated_user_id(request):
    if request.user.is_authenticated:
        return JsonResponse({"user_id": request.user.id})
    return JsonResponse({"error": _("User not authenticated")}, status=401)

def get_authenticated_user_object(request):
    user = request.user
    if user.is_authenticated:
        return JsonResponse({"user_object": {
            "user_id": user.id,
            "username": user.username,
            "avatar": user.avatar
        }})
    return JsonResponse({"error": _("User not authenticated")}, status=401)
