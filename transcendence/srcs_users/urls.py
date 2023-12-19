from django.urls import path, include
from .views import SignUpView, get_authenticated_user
from . import views

app_name = 'srcs_users' 

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('auth/user/', get_authenticated_user, name='get_authenticated_user'),
    path('oauth2/', views.home, name='home'),
    path('oauth2/login/', views.intra_login, name='intra_login'),
    path('oauth2/login/redirect/', views.intra_login_redirect, name='intra_login_redirect'),
    path('oauth2/logout/', views.logout, name='logout'),
]
    