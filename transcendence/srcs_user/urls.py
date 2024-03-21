from django.urls import path
from srcs_user import views

app_name = "srcs_user"

urlpatterns = [
    # path('oauth2/', views.test, name='oauth2'),
    path("users_list/", views.users_list, name="users_list"),
]
