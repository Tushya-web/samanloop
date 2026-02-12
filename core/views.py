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

    items = Item.objects.all().order_by('-created_at')[:4]
    categories = Category.objects.all()
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
    
    return render(request, "login.html")


def google_login_page(request):
    return render(request, "google_login.html")


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
    return render(request, "register.html", {"form": form})

def forgot_password(request):
    return render(request, "forgot_password.html")

def logout(request):
    auth_logout(request)
    return redirect("login")

def custom_csrf_failure(request, reason=""):
    return render(request, 'errors/csrf_error.html', status=403)

def error404(request):
    return render(request, 'errors/404.html', status=404)

def contact(request):
    return render(request, "contactsupport.html")

def about(request):
    return render(request, "About.html")

def pricingguide(request):
    return render(request, "pricingguide.html")

def howitworks(request):
    return render(request, "howwork.html")

def terms(request):
    return render(request, "terms.html")

def verify_page(request):
    return render(request, "verify.html")

def lender_dashboard(request):
    if not request.session.get("user"):
        return redirect("login")

    email = request.session["user"]
    user = User.objects.get(email=email)
    # 1. All items listed by this lender
    my_listings = Item.objects.filter(owner=user).order_by('-created_at')
    # 2. Incoming requests from others (Pending approval)
    incoming_requests = item_Request.objects.filter(item__owner=user, status='pending').order_by('-created_at')
    # 3. Active loops (Items currently out with borrowers)
    active_lending = item_usage.objects.filter(lender=user, status='active').order_by('-start_date')
    # 4. Lending History (Completed loops)
    lending_history = item_usage.objects.filter(lender=user, status='completed').order_by('-end_date')
    
    return render(request, "lender_dashboard.html", {
        "my_listings": my_listings,
        "incoming_requests": incoming_requests,
        "active_lending": active_lending,
        "lending_history": lending_history,
    })

def borrower_dashboard(request):
    # Ensure user is logged in via your session logic
    if not request.session.get("user"):
        return redirect("login")

    email = request.session["user"]
    user = User.objects.get(email=email)
    # 1. Requests sent by the borrower (Pending/Rejected/Accepted)
    sent_requests = item_Request.objects.filter(renter=user).order_by('-created_at')
    # 2. Items currently being used (Active Usage)
    active_usage = item_usage.objects.filter(renter=user, status='active').order_by('-start_date')
    # 3. Past rental history (Completed Usage)
    rental_history = item_usage.objects.filter(renter=user, status='completed').order_by('-end_date')
    return render(request, "borrower_dashboard.html", {
        "sent_requests": sent_requests,
        "active_usage": active_usage,
        "rental_history": rental_history,
    })

from django.db.models import Q
from django.shortcuts import render
from .models import Item, Category
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
    return render(request, "profile.html", {
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

    return render(request, "edit_profile.html", {"user": user})

def my_items(request):
    email = request.session.get("user")
    user = User.objects.get(email=email)

    items = Item.objects.filter(owner=user).only("id")

    return render(request, "my_items.html", {"items": items})


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

    return render(request, 'category_items.html', {
        'category': category,
        'all_categories': all_categories, # Necessary for the circular icons
        'items': items,
        'quality_choices': Item.QUALITY_CHOICES,
        'current_max': max_p or 5000,
        'selected_quality': quality, # To keep checkboxes checked after reload
    })

from core.models import Category

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

    return render(request, "add_item.html", {
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

        return render(request, "add_item_preview.html", {
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

    return render(request, "item_success.html", {
        "item": item
    })

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    images = item.images.all()
    reviews = Review.objects.filter(item=item).order_by('-created_at')
    today_date = now().date()

    return render(request, "item_detail.html", {
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

        return render(request, "request_item.html", {
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
        
        # Get data from hidden inputs
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        total_rent = request.POST.get("total_rent")
        
        # 1. Create the Request in Database
        item_Request.objects.create(
            item=item,
            renter=user, # Ensure user is logged in
            start_date=start_date,
            end_date=end_date,
            total_rent=total_rent,
            status="pending"
        )
        
        # 2. Trigger the Toast Message
        messages.success(request, f"Request for {item.name} sent successfully! The owner will respond soon.")
        
        # 3. Redirect to User's Dashboard or current page
        return redirect('item_detail', item_id=item.id)

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
            email = request.session["user"],
            user = User.objects.get(email=email),    
            reviewer=user,
            rating=rating,
            comment=comment
        )
        return redirect('item_detail', item_id=item_id)

def respond_to_request(request, request_id, action):

    if not request.session.get("user"):
        return redirect("login")

    email = request.session["user"]
    user = User.objects.get(email=email)

    rental_request = get_object_or_404(item_Request, id=request_id)

    if rental_request.item.owner != user:
        return redirect("lender_dashboard")

    if action == 'accept':
        rental_request.status = 'accepted'
        rental_request.save()

        item_usage.objects.create(
            item=rental_request.item,
            renter=rental_request.renter,
            lender=user,
            start_date=rental_request.start_date,
            end_date=rental_request.end_date,
            status='active'
        )

    elif action == 'reject':
        rental_request.status = 'rejected'
        rental_request.save()

    return redirect('lender_dashboard')

def browse_items(request):
    return render(request, "browse_items.html")

def wallet(request):
    return render(request, "wallet.html")
    
# @login_required
def add_money(request):
    if request.method == "POST":
        amount = float(request.POST["amount"])
        email = request.session["user"]
        user = User.objects.get(email=email)
        wallet = Wallet.objects.get(user=user)

        wallet.balance += amount
        wallet.save()

        WalletTransaction.objects.create(
            user=request.user,
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
                user=request.user,
                amount=amount,
                transaction_type="debit",
                description="Withdrawal Request"
            )

    return redirect("wallet")
