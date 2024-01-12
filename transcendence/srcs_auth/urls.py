from django.urls import path, include
from srcs_auth import views

app_name = 'srcs_auth' 

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/user/', views.get_authenticated_user, name='get_authenticated_user'),
    path('oauth2/login/', views.intra_login, name='intra_login'),
    path('oauth2/login/redirect/', views.intra_login_redirect, name='intra_login_redirect'),
    path('oauth2/logout/', views.logout_user, name='logout_user'),
]
