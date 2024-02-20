from django.urls import path

from .views import ChatView

app_name = 'srcs_chat' 

urlpatterns = [
    path('<int:room_id>/', ChatView.as_view(), name='open_chat'),
    path('create_or_open_chat/<int:user_id>/', ChatView.as_view(), name='create_or_open_chat'),

]