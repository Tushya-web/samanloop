from django.shortcuts import render

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