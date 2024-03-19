from django.urls import include, path

from .views import ChatView, GetUpdatedUserListView, ProfileView

app_name = "srcs_chat"

urlpatterns = [
    path("<int:room_id>/", ChatView.as_view(), name="open_chat"),
    path(
        "create_or_open_chat/<int:user_id>/",
        ChatView.as_view(),
        name="create_or_open_chat",
    ),
    path(
        "get_updated_user_list/",
        GetUpdatedUserListView.as_view(),
        name="get_updated_user_list",
    ),
    path(
        "user/",
        include(
            [
                # path(
                #     "blocked/<slug:username>",
                #     views.BlockedFormView.as_view(),
                #     name="blocked",
                # ),
                path("<slug:username>", ProfileView.as_view(), name="profile"),
            ]
        ),
    ),
]
