from django.urls import include, path

from .views import views

app_name = "srcs_chat"

unblocked_url = [
    path(
        "unblocked/",
        include(
            [
                path("", views.UnblockedFormView.as_view(), name="unblocked"),
                path("<slug:username>", views.UnblockedFormView.as_view()),
            ]
        ),
    )
]


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
    path("<int:room_id>/", views.ChatView.as_view(), name="open_chat"),
    path(
        "create_or_open_chat/<int:user_id>/",
        views.ChatView.as_view(),
        name="create_or_open_chat",
    ),
    path(
        "get_updated_user_list/",
        views.GetUpdatedUserListView.as_view(),
        name="get_updated_user_list",
    ),
    path(
        "user/",
        include(
            [
                *blocked_urls,
                *unblocked_url,
                path("<slug:username>", views.ProfileView.as_view(), name="profile"),
            ]
        ),
    ),
]
