from decimal import Decimal
import email
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from httpx import request

from core.forms import ItemCreateForm
from core.models import Category, Item, User,ItemImage, Wallet, WalletTransaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login 
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail


from .forms import RegisterForm
from .firebase_service import firebase_auth, auth, send_firebase_verification, send_firebase_verification_email

from .firebase_service import firebase_login



def index(request):

    user = None
    

    if request.session.get("user"):
        try:
            user = User.objects.get(email=request.session["user"])
        except:
            pass
        
    selected_city = request.session.get("selected_city")

    # If no city selected, fallback to first available city
    if not selected_city:
        first_item = Item.objects.first()
        if first_item:
            selected_city = first_item.city
            request.session["selected_city"] = selected_city

    # Filter items by selected city
    items = Item.objects.filter(
    city=selected_city
    ).order_by('-created_at')[:4]

    # Categories that have items in selected city
    categories = Category.objects.filter(
    items__city=selected_city
    ).distinct()

    
    return render(request, 'index.html', {'items': items, 'user': user, 'categories': categories})



def login(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        try:
            result = firebase_login(email, password)
            if "error" in result:
                messages.error(request, "Invalid email or password")
                return redirect("login")
            idToken = result["idToken"]
            
            info = firebase_auth.get_user_by_email(email)

            if not info.email_verified:
                
                send_firebase_verification(idToken)

                request.session["pending_email"] = email

                messages.info(
                    request,
                    "Verification email sent! Please verify before login."
                )
                return redirect("verify")
            
            user = User.objects.get(email=email)
            request.session["user"] = email
            next_url = request.GET.get("next") or "/profile/"
            User.email_verified = True
            return redirect(next_url)

        except User.DoesNotExist:
            messages.error(request, "Account not found")

        except Exception as e:
            print("LOGIN ERROR:", e)
            messages.error(request, "Invalid login")
    
    return render(request, "usera/login.html")


def google_login_page(request):
    return render(request, "usera/google_login.html")


def google_callback(request):
    data = json.loads(request.body)
    token = data.get("token")
    try:
        decoded = firebase_auth.verify_id_token(token)
        email = decoded["email"]
        name = decoded.get("name", "")
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
            }
        )
        request.session["user"] = email
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                if User.objects.filter(email=email).exists():
                    messages.error(request, "Email already registered")
                    return redirect("register")
                # Create Firebase user only
                firebase_auth.create_user(
                    email=email,
                    password=password,
                    display_name=form.cleaned_data["name"]
                )
                User.objects.create(
                    name=form.cleaned_data["name"],
                    email=email,
                    phone_number=form.cleaned_data["phone"]
                )
                messages.success(request, "Account created! Please login.")
                return redirect("login")
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = RegisterForm()
    return render(request, "usera/register.html", {"form": form})

def forgot_password(request):
    return render(request, "usera/forgot_password.html")

def logout(request):
    auth_logout(request)
    return redirect("login")

def custom_csrf_failure(request, reason=""):
    return render(request, 'errors/csrf_error.html', status=403)

def error404(request):
    return render(request, 'errors/404.html', status=404)

def contact(request):
    return render(request, "pages/contactsupport.html")

def about(request):
    return render(request, "pages/About.html")

def pricingguide(request):
    return render(request, "pages/pricingguide.html")

def howitworks(request):
    return render(request, "pages/howwork.html")

def terms(request):
    return render(request, "pages/terms.html")

def verify_page(request):
    return render(request, "usera/verify.html")



def lender_dashboard(request):
    if not request.session.get("user"):
        return redirect("login")

    today = timezone.now().date()
    
    email = request.session["user"]
    user = User.objects.get(email=email)
    user_wallet, _ = Wallet.objects.get_or_create(user=user)
    # 1. All items listed by this lender
    my_listings = Item.objects.filter(owner=user).order_by('-created_at')
    # 2. Incoming requests from others (Pending approval)
    incoming_requests = item_Request.objects.filter(item__owner=user).order_by('-created_at')
    # 3. Active loops (Items currently out with borrowers)
    active_lending = item_usage.objects.filter(lender=user,status__in=['active', 'returning']).order_by('-start_date')
    # 4. Lending History (Completed loops)
    lending_history = item_usage.objects.filter(lender=user, status='completed').order_by('-end_date')
    
    earning_logs = Payment.objects.filter(
    lender=user
    ).select_related("item_usage__item", "borrower").order_by("-payment_date")

    
    return render(request, "lender_dashboard.html", {
        "today": today,
        "wallet_balance": user_wallet.balance,
        "active_lending": active_lending,
        "my_listings": my_listings,
        "incoming_requests": incoming_requests,
        "active_lending": active_lending,
        "lending_history": lending_history,
        "earning_logs": earning_logs,
    })

from django.utils import timezone
from .models import User, item_Request, item_usage


def borrower_dashboard(request):
    if not request.session.get("user"):
        return redirect("login")

    email = request.session["user"]
    user = User.objects.get(email=email)
    
    sent_requests = item_Request.objects.filter(renter=user).order_by('-created_at')
    
    # active_usage should include both 'active' and 'returning' so the borrower sees the status
    active_usage = item_usage.objects.filter(
        renter=user, 
        status__in=['active', 'returning'] 
    ).order_by('-start_date')
    
    rental_history = item_usage.objects.filter(renter=user, status='completed').order_by('-end_date')
    
    # Pass 'today' to the template for the button logic
    today = timezone.now().date()
    
    return render(request, "borrower_dashboard.html", {
        "active_rentals": active_usage,
        "sent_requests": sent_requests,
        "active_usage": active_usage,
        "rental_history": rental_history,
        "today": today, 
    })

def initiate_return(request, usage_id):
    usage = get_object_or_404(
        item_usage, 
        id=usage_id, 
        renter__email=request.session['user']
    )

    today = timezone.now().date()

    if usage.status == 'active' and today >= usage.end_date:
        usage.status = 'returning'
        usage.save()

    return redirect('borrower_dashboard')


def confirm_return(request, usage_id):
    usage = get_object_or_404(item_usage, id=usage_id, lender__email=request.session['user'])
    
    with transaction.atomic():
        usage.status = 'completed'
        usage.save()
        
        # Make the item available for rent again
        item = usage.item
        # item.availability_status = "available" # or whatever your default string is
        # item.save()
    
    messages.success(request, "Return confirmed! The item is now listed as available again.")
    return redirect('lender_dashboard')

from django.db.models import Q
from django.shortcuts import render
from .models import Item, Category, Payment, Query
from django.db.models import Q


def browse_items(request):
    # 1. Fetch all items initially
    items = Item.objects.all()
    categories = Category.objects.all()

    # 2. Handle Search (Text search)
    query = request.GET.get('q')
    if query:
        items = items.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    # 3. Handle Category Filter (Pills)
    category_name = request.GET.get('category')
    if category_name:
        items = items.filter(category__name=category_name)

    # 4. Handle Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'low':
        items = items.order_by('rent_per_day')
    elif sort_by == 'high':
        items = items.order_by('-rent_per_day')
    else:
        items = items.order_by('-created_at') # Default to newest

    context = {
        'items': items,
        'categories': categories,
    }
    return render(request, 'browse_items.html', context)

from django.db.models import Q

def browse_items(request):

    # 🔹 Get selected city from session
    selected_city = request.session.get("selected_city")

    # 🔹 Start with city-filtered items
    if selected_city:
        items = Item.objects.filter(city=selected_city)
    else:
        items = Item.objects.all()

    categories = Category.objects.all()

    # 🔍 Handle Search
    query = request.GET.get('q')
    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query)
        )

    # 🎯 Handle Category Filter
    category_name = request.GET.get('category')
    if category_name:
        items = items.filter(category__name=category_name)

    # 💰 Handle Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'low':
        items = items.order_by('rent_per_day')
    elif sort_by == 'high':
        items = items.order_by('-rent_per_day')
    else:
        items = items.order_by('-created_at')

    context = {
        'items': items,
        'categories': categories,
        'selected_city': selected_city,
        'search_query': query,
    }

    return render(request, 'browse_items.html', context)

def check_verified(request):
    email = request.session.get("pending_email")
    
    if not email:
        return redirect("login")
    try:
        info = firebase_auth.get_user_by_email(email)

        if info.email_verified:
            messages.success(request, "Email verified! Please login.")
            return redirect("login")

        messages.error(request, "Not verified yet. Check your email.")
        return redirect("verify")
    except:
        return redirect("login")

def profile(request):
    # SIMPLE CHECK
    if not request.session.get("user"):
        return redirect("/login/?next=/profile/")
    email = request.session.get("user")
    user = User.objects.get(email=email)
    return render(request, "usera/profile.html", {
        "user": user
    })
    
def edit_profile(request):
    
    if not request.session.get("user"):
        return redirect("/login/")
    
    email = request.session["user"]
    user = User.objects.get(email=email)

    if request.method == "POST":
        phone = request.POST.get("phone")

        if not phone:
            messages.error(request, "Phone number missing")
            return redirect("edit_profile")
        user.name = request.POST.get("name")
        user.phone_number = phone
        user.city = request.POST.get("city") or ""
        user.address = request.POST.get("address") or ""
        
        if request.FILES.get("profile"):
            user.profile = request.FILES["profile"]
        user.save()
        
        messages.success(request, "Success! Your profile settings have been updated.")
        return redirect("profile")

    return render(request, "usera/edit_profile.html", {"user": user})

def my_items(request):
    email = request.session.get("user")
    user = User.objects.get(email=email)

    items = Item.objects.filter(owner=user).only("id")

    return render(request, "items/my_items.html", {"items": items})


def delete_item(request, id):
    if not request.session.get("user"):
        return redirect("/login/")

    email = request.session["user"]
    user = User.objects.get(email=email)
    
    item = get_object_or_404(Item, id=id, owner=user)
    item.delete()
    return redirect("my_items")

from core.models import Category, Item

def category_items(request, id):
    category = get_object_or_404(Category, id=id)
    # Get all categories for the top circular menu
    all_categories = Category.objects.all()
    
    items = Item.objects.filter(category=category)

    # --- FILTER LOGIC ---
    min_p = request.GET.get('min_price')
    max_p = request.GET.get('max_price')
    quality = request.GET.getlist('quality') # For checkboxes

    if min_p:
        items = items.filter(rent_per_day__gte=min_p)
    if max_p:
        items = items.filter(rent_per_day__lte=max_p)
    if quality:
        items = items.filter(quality__in=quality)
    
    # -----------------------------

    return render(request, 'items/category_items.html', {
        'category': category,
        'all_categories': all_categories, # Necessary for the circular icons
        'items': items,
        'quality_choices': Item.QUALITY_CHOICES,
        'current_max': max_p or 5000,
        'selected_quality': quality, # To keep checkboxes checked after reload
    })

from core.models import Category

def set_city(request, city):
    request.session["selected_city"] = city
    return JsonResponse({"status": "success"})

def add_item(request):
    email = request.session.get("user")
    if not email:
        return redirect("login")

    user = User.objects.get(email=email)

    if request.method == "POST":

        # 🔥 Get category from POST
        category_id = request.POST.get("category")
        category_obj = Category.objects.get(id=category_id)

        item = Item.objects.create(
            owner=user,
            category=category_obj,  # ✅ Correct
            name=request.POST["name"],
            description=request.POST["description"],
            brand=request.POST.get("brand", ""),
            purchase_price=request.POST["purchase_price"],
            purchase_year=request.POST["purchase_year"],
            quality=request.POST["quality"],
            rent_per_day=request.POST["rent_per_day"],
            deposit_amount=request.POST.get("deposit_amount", 0),
            allow_delivery="allow_delivery" in request.POST,
            self_pickup="self_pickup" in request.POST,
            latitude=request.POST.get("latitude", ""),
            longitude=request.POST.get("longitude", ""),
            city=user.city,
        )

        # 🔥 Multiple images
        for img in request.FILES.getlist("images"):
            ItemImage.objects.create(
                item=item,
                image=img
            )

        return redirect("my_items")

    # GET request
    categories = Category.objects.all()

    return render(request, "items/add_item.html", {
        "user_city": user.city,
        "categories": categories
    })

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def preview_item(request):

    if not request.session.get("user"):
        return redirect("/login/")

    email = request.session["user"]
    user = User.objects.get(email=email)

    if request.method == "POST":

        category_id = request.POST.get("category")

        if not category_id:
            return redirect("add_item")  # safety

        category_obj = Category.objects.get(id=category_id)

        request.session['item_data'] = {
            "name": request.POST.get("name"),
            "category_id": category_obj.id,
            "category_name": category_obj.name,
            "brand": request.POST.get("brand"),
            "purchase_price": request.POST.get("purchase_price"),
            "purchase_year": request.POST.get("purchase_year"),
            "description": request.POST.get("description"),
            "quality": request.POST.get("quality"),
            "latitude": request.POST.get("latitude"),
            "longitude": request.POST.get("longitude"),
            "allow_delivery": bool(request.POST.get("allow_delivery")),
            "self_pickup": bool(request.POST.get("self_pickup")),
            "rent_per_day": request.POST.get("rent_per_day"),
            "deposit_amount": request.POST.get("deposit_amount"),
            "city": user.city,
        }

        # Save images temporarily
        images = request.FILES.getlist("images")
        request.session['temp_images'] = []

        for img in images:
            path = default_storage.save(
                f"temp/{img.name}",
                ContentFile(img.read())
            )
            request.session['temp_images'].append(path)

        return render(request, "items/add_item_preview.html", {
            "data": request.session['item_data'],
            "images": request.session['temp_images'],
            "category_obj": category_obj,
        })

    return redirect("add_item")

from decimal import Decimal
from .models import Category, Review, item_Request, item_usage


def confirm_item(request):
    if not request.session.get("user"):
        return redirect("/login/")
    email = request.session["user"]
    user = User.objects.get(email=email)
    data = request.session.get("item_data")
    images = request.session.get("temp_images")
    if not data:
        return redirect("add_item")

    # 🔥 GET CATEGORY
    category_id = data.get("category_id")
    if not category_id:
        return redirect("add_item")

    category_obj = Category.objects.get(id=category_id)

    # 🔐 SAFE DECIMAL CONVERSION
    try:
        purchase_price = Decimal(data.get("purchase_price"))
    except:
        purchase_price = Decimal("0.00")

    try:
        rent_per_day = Decimal(data.get("rent_per_day"))
    except:
        rent_per_day = Decimal("0.00")

    deposit_raw = data.get("deposit_amount")
    try:
        deposit_amount = Decimal(deposit_raw) if deposit_raw else Decimal("0.00")
    except:
        deposit_amount = Decimal("0.00")

    try:
        purchase_year = int(data.get("purchase_year"))
    except:
        purchase_year = 2024

    # ✅ CREATE ITEM (NOW WITH CATEGORY)
    item = Item.objects.create(
        owner=user,
        category=category_obj,  # 🔥 THIS WAS MISSING
        name=data.get("name"),
        brand=data.get("brand"),
        purchase_price=purchase_price,
        purchase_year=purchase_year,
        description=data.get("description"),
        quality=data.get("quality"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        allow_delivery=data.get("allow_delivery"),
        self_pickup=data.get("self_pickup"),
        rent_per_day=rent_per_day,
        deposit_amount=deposit_amount,
        city=data.get("city"),
    )

    # 🔥 SAVE IMAGES
    if images:
        for img in images:
            ItemImage.objects.create(
                item=item,
                image=img
            )

    # 🧹 CLEAR SESSION
    request.session.pop("item_data", None)
    request.session.pop("temp_images", None)

    return redirect("item_success", item_id=item.id)

from django.utils.timezone import now

def item_success(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    return render(request, "items/item_success_added.html", {
        "item": item
    })



from .forms import ItemForm
def edit_item(request, item_id):
    email = request.session.get("user")
    user = User.objects.get(email=email)

    item = get_object_or_404(Item, id=item_id, owner=user)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            item = form.save()

            # 🔥 SAVE NEW IMAGE
            if request.FILES.get("images"):
                for img in request.FILES.getlist("images"):
                    ItemImage.objects.create(item=item, image=img)

            return redirect("my_items")

        else:
            print(form.errors)

    else:
        form = ItemForm(instance=item)

    return render(request, "items/edit_item.html", {"form": form, "item": item})


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    images = item.images.all()
    reviews = Review.objects.filter(item=item).order_by('-created_at')
    today_date = now().date()

    return render(request, "items/item_detail.html", {
        "item": item,
        "images": images,
        "reviews": reviews,
        "today_date": today_date,
        "owner": item.owner,
    })


from datetime import datetime

def request_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if not request.session.get("user"):
        return redirect("login")

    # If coming from the Detail Page (POST)
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        
        # Calculate days for display
        d1 = datetime.strptime(start_date, "%Y-%m-%d")
        d2 = datetime.strptime(end_date, "%Y-%m-%d")
        total_days = (d2 - d1).days + 1
        total_rent = total_days * float(item.rent_per_day)
        grand_total = total_rent + float(item.deposit_amount)

        return render(request, "items/request_item.html", {
            "item": item,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "total_rent": total_rent,
            "grand_total": grand_total
        })
    
    # If accessed directly without dates, redirect back
    return redirect('item_detail', item_id=item_id)


def finalize_request(request, item_id):

    email = request.session["user"]
    user = User.objects.get(email=email)

    if request.method == "POST":
        item = get_object_or_404(Item, id=item_id)

        start_date = datetime.strptime(request.POST.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.POST.get("end_date"), "%Y-%m-%d").date()

        total_days = (end_date - start_date).days + 1
        total_rent = total_days * float(item.rent_per_day)
        grand_total = total_rent + float(item.deposit_amount)

        # 🔥 CHECK CONFLICT IN ACTIVE USAGE
        conflict = item_usage.objects.filter(
            item=item,
            status__in=["active", "returning"]
        ).filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()

        # 🔥 CHECK CONFLICT IN REQUESTS
        request_conflict = item_Request.objects.filter(
            item=item,
            status__in=["pending", "accepted", "paid"]
        ).filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()

        if conflict or request_conflict:
            messages.error(request, "⚠ This item is already booked for selected dates.")

            return render(request, "items/request_item.html", {
                "item": item,
                "start_date": start_date,
                "end_date": end_date,
                "total_days": total_days,
                "total_rent": total_rent,
                "grand_total": grand_total
            })

        # ✅ CREATE REQUEST
        item_Request.objects.create(
            item=item,
            renter=user,
            start_date=start_date,
            end_date=end_date,
            total_rent=total_rent,
            status="pending"
        )

        messages.success(request, f"Request for {item.name} sent successfully!")

        return redirect("item_detail", item_id=item.id)

def submit_review(request, item_id):
    email = request.session["user"]
    user = User.objects.get(email=email)


    if request.method == "POST":
        item = get_object_or_404(Item, id=item_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Create the review
        Review.objects.create(
            item=item,
            reviewer=user,
            rating=rating,
            comment=comment
        )
        return redirect('item_detail', item_id=item_id)

def respond_to_request(request, request_id, action):

    email = request.session.get("user")
    user = User.objects.get(email=email)

    rental_request = get_object_or_404(item_Request, id=request_id)

    if rental_request.item.owner != user:
        return redirect("lender_dashboard")

    if action == "accept":
        rental_request.status = "accepted"
        rental_request.save()

    elif action == "reject":
        rental_request.status = "rejected"
        rental_request.save()

    return redirect("lender_dashboard")

from django.db import transaction

def payment_page(request, request_id):

    email = request.session.get("user")
    user = User.objects.get(email=email)

    req = get_object_or_404(
        item_Request,
        id=request_id,
        renter=user
    )

    # 🔒 prevent double payment
    if req.status != "accepted":
        messages.error(request, "This request is not available for payment.")
        return redirect("borrower_dashboard")

    wallet, _ = Wallet.objects.get_or_create(user=user)

    total_amount = req.total_rent + req.item.deposit_amount

    if request.method == "POST":

        payment_mode = request.POST.get("payment_mode")

        # =========================
        # 💰 WALLET PAYMENT
        # =========================
        if payment_mode == "wallet":

            if wallet.balance < total_amount:
                messages.error(request, "Not enough wallet balance.")
                return redirect("payment_page", request_id=req.id)

            owner_wallet, _ = Wallet.objects.get_or_create(
                user=req.item.owner
            )

            with transaction.atomic():
            
                # 🔻 Deduct from borrower
                wallet.balance -= total_amount
                wallet.save()

                WalletTransaction.objects.create(
                    user=user,
                    amount=total_amount,
                    transaction_type="debit",
                    description=f"Rental payment for {req.item.name}"
                )

                # 🔺 Add rent to owner (NOT deposit)
                owner_wallet.balance += req.total_rent
                owner_wallet.save()

                WalletTransaction.objects.create(
                    user=req.item.owner,
                    amount=req.total_rent,
                    transaction_type="credit",
                    description=f"Rental income from {req.item.name}"
                )

                # 💳 Mark request paid
                req.status = "paid"
                req.payment_status = "paid"
                req.payment_id = "WALLET_TXN"
                req.save()
        
        elif payment_mode == "external":

            req.status = "paid"
            req.payment_status = "paid"
            req.payment_id = "EXT_TEST_123"
            req.save()

        else:
            messages.error(request, "Invalid payment method.")
            return redirect("payment_page", request_id=req.id)

        # =========================
        # CREATE ACTIVE USAGE
        # =========================
        if not item_usage.objects.filter(
            item=req.item,
            renter=req.renter,
            status="active"
        ).exists():
        
            usage = item_usage.objects.create(
                item=req.item,
                lender=req.item.owner,
                renter=req.renter,
                start_date=req.start_date,
                end_date=req.end_date,
                status="active"
            )
        
            # 💰 CREATE PAYMENT RECORD (ADD HERE)
            Payment.objects.create(
                item_usage=usage,
                lender=req.item.owner,
                borrower=req.renter,
                payment_amt=req.total_rent,
                deposit=req.item.deposit_amount,
                deposit_status=False
            )
        
        # req.item.availability_status = "in use"
        # req.item.save()

        messages.success(request, "Payment successful!")
        return redirect("borrower_dashboard")

    return render(request, "payment_page.html", {
        "req": req,
        "wallet": wallet,
        "total_amount": total_amount
    })



def wallet(request):
    return render(request, "wallet.html")
    
# @login_required
def add_money(request):
    if request.method == "POST":
        amount = float(request.POST["amount"])
        
        user = User.objects.get(email=request.session["user"])
        email = request.session["user"]
        wallet, _ = Wallet.objects.get_or_create(user=user)

        wallet.balance += amount
        wallet.save()

        WalletTransaction.objects.create(
        user=user,
        amount=amount,
        transaction_type="credit",
        description="Wallet Top-up"
    )


    return redirect("wallet")


# @login_required
def withdraw_money(request):
    if request.method == "POST":
        amount = float(request.POST["amount"])
        email = request.session["user"]
        user = User.objects.get(email=email)
        wallet = Wallet.objects.get(user=user)

        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()

            WalletTransaction.objects.create(
                user=user,
                amount=amount,
                transaction_type="debit",
                description="Withdrawal Request"
            )

    return redirect("wallet")

def report_issue(request, item_id=None):
    email = request.session.get("user")
    if not email:
        return redirect("login")

    user = User.objects.get(email=email)
    
    # Fetch items currently being used by the user for the dropdown
    # We filter 'item_usage' where the renter is the user and status is active
    active_rentals = item_usage.objects.filter(renter=user, status='active').select_related('item')
    user_items = [usage.item for usage in active_rentals]

    item = None
    if item_id:
        item = get_object_or_404(Item, id=item_id)

    report_history = Query.objects.filter(user=user).order_by('-created_at')

    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        # Get item from the dropdown if not provided in URL
        selected_item_id = request.POST.get("selected_item")
        
        final_item = item
        if not final_item and selected_item_id:
            final_item = get_object_or_404(Item, id=selected_item_id)

        Query.objects.create(
            user=user,
            item=final_item,
            subject=subject,
            message=message,
            status="open"
        )

        messages.success(request, "Your report has been logged and sent to the Admin team.")
        return redirect("report_issue")

    return render(request, "report_page.html", {
        "item": item,
        "user_items": user_items,
        "history": report_history
    })