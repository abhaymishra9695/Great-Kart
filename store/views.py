from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import *
from carts.views import _cart_id
from django.http import HttpResponse 
from django.db.models import Q 
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
    context={
        'single_product':single_product,
        'in_cart':in_cart
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
