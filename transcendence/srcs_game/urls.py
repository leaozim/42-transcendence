from django.urls import path
from . import views

app_name = "srcs_game"

urlpatterns = [
    # path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
]