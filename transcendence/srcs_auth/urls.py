from django.urls import path, include
from srcs_auth import views
from srcs_auth.auth_two_factor import TOTPCreateView, TOTPVerifyView, TOTPDeleteView

app_name = 'srcs_auth' 

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/user/', views.get_authenticated_user, name='get_authenticated_user'),
    path('oauth2/login/', views.intra_login, name='intra_login'),
    path('oauth2/login/redirect/', views.intra_login_redirect, name='intra_login_redirect'),
    path('oauth2/logout/', views.logout_user, name='logout_user'),
    path('oauth2/refresh_token/', views.refresh_token, name='refresh_token'),
    path('totp/create/', TOTPCreateView.as_view(), name='totp-create'),
    path('totp/login/<str:token>/', TOTPVerifyView.as_view(), name='totp-login'),
    path('totp/delete/', TOTPDeleteView.as_view(), name='totp-delete'),
    path('test-form/', views.test_form_view, name='test_form'),


]
