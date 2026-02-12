from core.models import User

def get_logged_user(request):

    email = request.session.get("user")

    if not email:
        return None

    try:
        return User.objects.get(email=email)
    except:
        return None
    
    