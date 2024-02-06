import os

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.template import loader

from srcs_auth.decorators import two_factor_required
from srcs_auth.jwt_token import (
    verify_jwt_token,
    generate_jwt_token,
    JWTVerificationFailed,
)
from srcs_auth.forms import UserCreationForm, UserLoginForm
from srcs_auth.auth import IntraAuthenticationBackend
from srcs_auth.services import TOTPService, exchange_code


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "account/signup.html"


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True


@two_factor_required
def get_authenticated_user(request):
    if request.user.is_authenticated:
        return redirect("home")
        # return HttpResponse(render(request=request, template_name="login/login.html"))

    return JsonResponse({"error": "Usuário não autenticado"}, status=401)


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

    return JsonResponse({"error": "Erro ao atualizar o token"}, status=400)


class TOTPCreateView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        totp_service = TOTPService()

        qr_code, totp_code = totp_service.create_totp_code(user)
        return render(
            request,
            "registration/totp_create_2f.html",
            {"qrcode": qr_code, "totp_code": totp_code},
        )


class TOTPVerifyView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, token):
        user = request.user
        totp_service = TOTPService()

        if totp_service.verify_totp_token(user, token):
            response = JsonResponse({"success": True}, status=200)
            response.set_cookie(
                "two_factor",
                True,
                max_age=3600,
                secure=True,
                httponly=True,
                samesite="Lax",
            )
            return response

        return JsonResponse({"error": "Invalid token"}, status=400)


class TOTPDeleteView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        totp_service = TOTPService()

        if totp_service.delete_totp_devices(user):
            return JsonResponse({'success': 'TOTP devices deleted successfully'}, status=200)

def validate_token_2f(request):
    return render(request, "registration/validate_token_2f.html")
