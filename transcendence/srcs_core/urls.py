# Local folder
from . import views

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', views.IndexView, name='home'),
    path('admin/', admin.site.urls),
    path('', include(('srcs_user.urls', 'srcs_user'))),
]
