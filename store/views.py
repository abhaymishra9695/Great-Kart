from django.shortcuts import render, get_object_or_404,redirect
from .models import Product,ReviewRating,ProductGallery
from category.models import Category
from carts.models import *
from carts.views import _cart_id
from django.http import HttpResponse 
from django.db.models import Q 
from django.contrib import messages,auth
from orders.models import OrderProduct


from .forms import ReviewForm

# Create your views here.

def store(request,categories_slug=None):
    categories=None
    products=None
    if categories_slug!=None:
        categories=get_object_or_404(Category,slug=categories_slug)
        products=Product.objects.filter(category=categories,is_available=True)
    else:    
        products=Product.objects.all().filter(is_available=True)
    
    context={
        'products':products,
        'products_count':products.count()
    }
    
    return render(request,'store/store.html',context)

def product_detail(request,categories_slug,product_slug):

    try:
        category = Category.objects.get(slug=categories_slug)
        single_product = Product.objects.get(category=category, slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request)).exists()
    except Exception as e:
        raise e
    
    try:
        orderproduct=OrderProduct.objects.filter(user=request.user,product=single_product).exists()
    except:
        orderproduct=None
    # Get review
    reviews=ReviewRating.objects.filter(product=single_product,status=True) 
    product_gallery=ProductGallery.objects.filter(product=single_product)
    context={
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery
    }
    return render(request,'store/product_detail.html',context)

def search(request):
    if 'keywords' in request.GET:
        keyword = request.GET['keywords']
        if keyword:
            products=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))         

    context={
    'products':products,
    'products_count':products.count()
    }
    return render(request,'store/store.html',context)



def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=product_id)
    print("user:-",request.user.id)
    if request.method == "POST":
        try:
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            print("review:-",review)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, "Thank you! Your review has been updated.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                # data = form.save(commit=False) or
                data=ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product = product
                data.user = request.user
                data.save()
                messages.success(request, "Thank you! Your review has been submitted.")
            return redirect(url)
