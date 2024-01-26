from django.urls import path

from . import views

app_name = 'srcs_chat' 

urlpatterns = [
    path("", views.index, name="index"),
    path('list_users/', views.list_users, name='list_users'),
    # path('open_chat/<int:user_id_2>/', views.open_chat, name='open_chat'),
    path("<str:room_name>/", views.room, name="room"),
    # path('create_room/', views.create_room, name='create_room'),

    path('create_or_open_chat/<int:user_id>/', views.create_or_open_chat, name='create_or_open_chat'),

]