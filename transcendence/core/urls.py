# from django.contrib import admin
# from django.urls import include, path
# from . import views 

# urlpatterns = [
#     path("users/", include("users.urls")),
#     path("admin/", admin.site.urls),
#     path("", views.index, name="index"),  
# ]

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('users/', include(('users.urls', 'users'))),
    path('users/', include('django.contrib.auth.urls')),
]