from django.urls import path
from srcs_tournament import views

urlpatterns = [
    # path("tournament/", views.UserList.as_view(), name="index"),
    path("create_tournament/", views.create_tournament, name="create_tournament"),
    path(
        "tournament_player_invite/<int:user_id>/", views.users_list, name="users_list"
    ),
    path("tournament_player_invite/", views.users_list, name="users_list"),
    path(
        "tournament_player_invite/<int:user_id>/<int:user_accept_id>/",
        views.user_accept,
        name="user_accept",
    ),
    path(
        "tournament-alias/",
        views.create_tournament_alias,
        name="create_tournament_alias",
    ),
]

