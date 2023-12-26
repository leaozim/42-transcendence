from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('', include(('srcs_user.urls', 'srcs_user'))),
]
