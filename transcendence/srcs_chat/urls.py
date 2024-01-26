from django.urls import path

from . import views

app_name = 'srcs_chat' 

urlpatterns = [
    path("", views.chats_list, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path('create_or_open_chat/<int:user_id>/', views.create_or_open_chat, name='create_or_open_chat'),

]