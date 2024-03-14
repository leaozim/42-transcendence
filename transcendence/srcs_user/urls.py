from django.urls import include, path
from srcs_user import views

app_name = "srcs_user"

urlpatterns = [
    # path('oauth2/', views.test, name='oauth2'),
    path("users_list/", views.users_list, name="users_list"),
    path(
        "user/",
        include(
            [
                path("blocked/", views.BlockedFormView.as_view(), name="blocked"),
            ]
        ),
    ),
]
