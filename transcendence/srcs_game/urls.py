from django.urls import path
from . import views

app_name = "srcs_game"

urlpatterns = [
    path("<int:room_id>/", views.room, name="room"),
    path('create_game/<int:right_player_id>/', views.create_game_view, name='create_game'),
    path('computer/', views.create_computer_game_view, name='computer'),
    path('<int:room_id>/cancel/', views.cancel_game_view, name='cancel'),
    path('open/', views.open_games_view, name='open_games'),
    path("", views.UserList.as_view(), name="index"),
]