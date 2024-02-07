from django.urls import path
from srcs_auth import views

app_name = "srcs_auth"

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login-django"),
    path("auth/user/", views.get_authenticated_user, name="get_authenticated_user"),
    path("oauth2/login/", views.intra_login, name="intra_login"),
    path(
        "oauth2/login/redirect/",
        views.intra_login_redirect,
        name="intra_login_redirect",
    ),
    path("oauth2/logout/", views.logout_user, name="logout_user"),
    path("oauth2/refresh_token/", views.refresh_token, name="refresh_token"),
    path("totp/create/", views.TOTPCreateView.as_view(), name="totp-create"),
    path("totp/user/", views.TOTPVerifyView.get, name="totp-verify"),
    path("totp/login/<str:token>/", views.TOTPVerifyView.as_view(), name="totp-login"),
    path("totp/delete/", views.TOTPDeleteView.as_view(), name="totp-delete"),
    path("validate_token_2f/", views.validate_token_2f, name="validate_token_2f"),
]
