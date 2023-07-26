from django.shortcuts import render,redirect

# Create your views here.
from django.http import HttpResponse
from carts.models import *
def place_order(request):
    current_user=request.user 
    # if cart count is less than or equal to 0 then redirect back to shop
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count <=0:
        return redirect('store')