from django.conf import settings
from core import views
from django.contrib import admin
from django.urls import path
from core.views import about , add_money , error404, logout, contact, howitworks, index, pricingguide, terms, login, register, profile , add_item, verify_page, wallet, withdraw_money, browse_items

from django.conf.urls.static import static

urlpatterns = [
    
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('admin/logout/', admin.site.logout, name='logout'),
    
    path('#/', error404, name='error404'),
    
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('verify/', verify_page, name='verify'),

    path('forgot/', views.forgot_password, name='forgot_password'),
    
    path("google-login/", views.google_login_page , name="google_login"),
    path("google-callback/", views.google_callback, name="google_callback"),
    

    
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    
    path('borrower_dashboard/', views.borrower_dashboard, name='borrower_dashboard'),
    
    path('payment_page/<int:request_id>/', views.payment_page, name='payment_page'),
    
    path('request/<int:request_id>/<str:action>/', views.respond_to_request, name='respond_to_request'),
    
    path('lender-dashboard/', views.lender_dashboard, name='lender_dashboard'),
    
        # Initiate Return
    path("initiate-return/<int:usage_id>/", views.initiate_return, name="initiate_return"),
    
    # Confirm Return (Lender)
    path("confirm-return/<int:usage_id>/", views.confirm_return, name="confirm_return"),

    # 2. The Finalize Request (POST action from the confirmation page)
    path('item/<int:item_id>/finalize/', views.finalize_request, name='finalize_request'),

    # 3. Submit Review (POST action from the detail page)
    path('item/<int:item_id>/submit-review/', views.submit_review, name='submit_review'),
    
    # 4. Request Item (The confirmation page with the price breakdown)
    path('item/<int:item_id>/request/', views.request_item, name='request_item'),

    path("my_items/", views.my_items, name="my_items"),
    path("items/edit/<int:item_id>/", views.edit_item, name="edit_item"),
    
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path("item/delete/<int:id>/", views.delete_item, name="delete_item"),
    
    path("category/<int:id>/", views.category_items, name="category_items"),
    
    path("item/<int:item_id>/", views.item_detail, name="item_detail"),

    path("item/<int:item_id>/rent/", views.request_item, name="request_item"),

    path('item/<int:item_id>/review/', views.submit_review, name='submit_review'),
    path('item/<int:item_id>/finalize_request/', views.finalize_request, name='finalize_request'),

    
    path('wallet/', wallet, name='wallet'),
    path("wallet/add/", add_money, name="wallet_add_money"),
    path("wallet/withdraw/", withdraw_money, name="wallet_withdraw"),

    
    path('add-item/', add_item, name='add_item'),
    path("set-city/<str:city>/", views.set_city, name="set_city"),
    path('preview-item/', views.preview_item, name='preview_item'),
    path("confirm/", views.confirm_item, name="confirm_item"),
    path("item_success/<int:item_id>/", views.item_success, name="item_success"),
    
    path("report/", views.report_issue, name="report_issue"),
    path("report/<int:item_id>/", views.report_issue, name="report_item"),
    
    path('browse-items/', browse_items, name='browse_items'),
    path('about/', about, name='about'),    
    path('contact/', contact, name='contact'),
    path('pricingguide/', pricingguide, name='pricingguide'),
    path('howitworks/', howitworks, name='howitworks'),
    path('terms/', terms, name='terms'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)