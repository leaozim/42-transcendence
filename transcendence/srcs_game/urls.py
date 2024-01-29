from django.urls import path
from . import views

app_name = "srcs_game"

urlpatterns = [
    path("<str:room_name>/", views.room, name="room"),
    path('create_game/<int:right_player_id>/', views.create_game_view, name='create_game'),
]