from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from two_factor.urls import urlpatterns as two_factor_urls


urlpatterns = [
    path('', TemplateView.as_view(template_name='login.html'), name='login'),
    path('admin/', admin.site.urls, name='admin'),
    path('', include(('srcs_user.urls', 'srcs_user'))),
    path('', include(('srcs_auth.urls', 'srcs_auth'))),
    path("chat/", include("srcs_chat.urls")),
    path('', include(two_factor_urls)),


]
