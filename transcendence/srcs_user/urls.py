from django.urls import include, path
from srcs_user import views

app_name = "srcs_user"

blocked_urls = [
    path(
        "blocked/",
        include(
            [
                path("", views.BlockedFormView.as_view(), name="blocked"),
                path("<slug:username>", views.BlockedFormView.as_view()),
            ]
        ),
    )
]

urlpatterns = [
    # path('oauth2/', views.test, name='oauth2'),
    path("users_list/", views.users_list, name="users_list"),
    path(
        "user/",
        include(blocked_urls),
    ),
]
