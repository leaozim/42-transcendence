from django.urls import path
from srcs_tournament import views

urlpatterns = [
    path('create_tournament/', views.create_tournament, name='create_tournament'),
    path('tournament_player_invite/<int:user_id>/', views.users_list, name='users_list'),
    path('tournament_player_invite/', views.users_list, name='users_list'),
]