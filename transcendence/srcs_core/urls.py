# Third party
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),

    path('admin/', admin.site.urls),

    path('', include(('srcs_user.urls', 'srcs_user'))),
    path('', include(('srcs_auth.urls', 'srcs_auth'))),
    path('', include('srcs_home.urls', 'srcs_home')),
    path("chat/", include("srcs_chat.urls")),
    path('game/', include('srcs_game.urls')),
]
