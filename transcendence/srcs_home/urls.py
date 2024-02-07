# Third Party
from django.urls import path

# Local Folder
from . import views

app_name = 'srcs_home'

urlpatterns = [
    # The home page can be acessed either from / or /home
    path('', views.IndexView.as_view(), name='home'),
    path('home', views.IndexView.as_view(), name='home')
    ]

