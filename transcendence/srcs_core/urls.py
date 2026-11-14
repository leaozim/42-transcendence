# Third party
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from srcs_core.env import env_bool
from srcs_auth.views import PasswordLoginView

urlpatterns = [
    # Django's stock login view would skip the two-factor step; use ours instead.
    path("accounts/login/", PasswordLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("", include(("srcs_user.urls", "srcs_user"))),
    path("", include(("srcs_auth.urls", "srcs_auth"))),
    path("", include("srcs_home.urls", "srcs_home")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("chat/", include("srcs_chat.urls")),
    path('game/', include('srcs_game.urls')),
    path('', include(('srcs_tournament.urls', 'srcs_tournament')))
]


def serve_media(request, path):
    return serve(request, path, document_root=settings.MEDIA_ROOT)


# Uploaded avatars. Without a reverse proxy (the default) the app serves them
# itself; set SERVE_MEDIA=false when nginx serves MEDIA_ROOT (see nginx/pong.conf).
if env_bool("SERVE_MEDIA", True):
    urlpatterns += [
        re_path(r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"), serve_media),
    ]
