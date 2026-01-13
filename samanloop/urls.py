from django.contrib import admin
from django.urls import path
from core.views import index, terms

urlpatterns = [
    path('', index, name='home'),
    path('admin/', admin.site.urls),
    path('terms/', terms, name='terms'),
]
