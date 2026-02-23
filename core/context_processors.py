from .models import Item

def cities_with_items(request):
    cities = (
        Item.objects
        .filter(availability_status="available")
        .values_list("city", flat=True)
        .distinct()
    )

    selected_city = request.session.get("selected_city")

    return {
        "navbar_cities": cities,
        "selected_city": selected_city
    }