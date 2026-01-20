from django.contrib import admin
from django.urls import path
from core.views import add_money, index, terms, login, register, verify, verified, account_hub , add_item , wallet, withdraw_money

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('verify/', verify, name='verify'),
    path('verified/', verified, name='verified'),
    
    path("account-hub/", account_hub, name="account_hub"),
    
    path('wallet/', wallet, name='wallet'),
    path("wallet/add/", add_money, name="wallet_add_money"),
    path("wallet/withdraw/", withdraw_money, name="wallet_withdraw"),

    
    path('add-item/', add_item, name='add_item'),
    
    path('terms/', terms, name='terms'),
]
