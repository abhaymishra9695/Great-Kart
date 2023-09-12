from django.shortcuts import render
from store.models import Product
from store.models import ReviewRating
def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('-created_date')
    reviews_dict = {}  # Create an empty dictionary to store reviews for each product

    for product in products:
        try:
            reviews = ReviewRating.objects.filter(product=product, status=True)
            reviews_dict[product.id] = reviews  # Store reviews in the dictionary with product IDs as keys
        except ReviewRating.DoesNotExist:
            reviews_dict[product.id] = []  # Handle the case when no reviews are found for a product

    context = {
        'products': products,
        'reviews_dict': reviews_dict  # Pass the dictionary containing reviews to the template
    }

    return render(request, 'home.html', context)
