from django.shortcuts import redirect, render

from core.forms import ItemCreateForm
from core.models import ItemImage

def index(request):
    return render(request, "index.html")

def terms(request):
    return render(request, "terms.html")

def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def verify(request):
    return render(request, "verify.html")

def verified(request):
    return render(request, "verified.html")

def account_hub(request):
    user = request.user

    context = {
        "user": user,
        "trust_score": "High",
        "rating": 4.8,
        "total_rentals": 27,

        # Dummy data (replace with DB queries)
        "listed_items": [],
        "borrowed_items": [],
        "active_rentals": [],
        "issues": [],
    }

    return render(request, "account_hub.html", context)

def add_item(request):
    if request.method == "POST":
        form = ItemCreateForm(request.POST)
        images = request.FILES.getlist("images")

        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()

            for img in images:
                ItemImage.objects.create(item=item, image=img)

            return redirect("account_hub")

    else:
        form = ItemCreateForm()

    return render(request, "add_item.html", {"form": form})