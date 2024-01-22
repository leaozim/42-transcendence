# Local folder
from . import views

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView


urlpatterns = [
    path('', views.IndexView, name='home'),
    path('admin/', admin.site.urls),
    path('', include(('srcs_user.urls', 'srcs_user'))),
    path('', include(('srcs_auth.urls', 'srcs_auth'))),
    path("chat/", include("srcs_chat.urls")),
]
