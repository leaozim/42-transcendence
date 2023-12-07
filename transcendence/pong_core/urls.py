from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('pong_users/', include(('pong_users.urls', 'pong_users'))),
    path('pong_users/', include('django.contrib.auth.urls')),
]