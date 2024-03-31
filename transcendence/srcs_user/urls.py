from django.urls import include, path
from srcs_user import views

app_name = "srcs_user"

urlpatterns = [
    path("users_list/", views.users_list, name="users_list"),
    path("user/", include([path("", views.get_id, name="me")])),
    path('check_blocked_user/', views.check_blocked_user, name='check_blocked_user'),
]
