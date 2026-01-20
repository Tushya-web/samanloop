from django.contrib import admin
from django.urls import path
from core.views import index, terms, login, register, verify, verified, account_hub

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('verify/', verify, name='verify'),
    path('verified/', verified, name='verified'),
    
    path("account-hub/", account_hub, name="account_hub"),
    
    path('terms/', terms, name='terms'),
]
