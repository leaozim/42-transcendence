from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from srcs_users import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('oauth2/', views.home, name='oauth2'),
    path('oauth2/login/', views.intra_login, name='intra_login'),
    path('oauth2/login/redirect', views.intra_login_redirect, name='intra_login_redirect'),

    # path('srcs_users/', include(('srcs_users.urls', 'srcs_users'))),
    # path('srcs_users/', include('django.contrib.auth.urls')),
]