from .models import *
from .views import _cart_id
import datetime
import git
from django.conf import settings
def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)
    


def date_context_processor(request):
    current_datetime = datetime.datetime.now()
    repo = git.Repo(settings.BASE_DIR)
            
    return {
       'current_date': current_datetime.day,
        'current_month': current_datetime.month,
        'current_year': current_datetime.year,
        'current_day':current_datetime.strftime('%A'),
        'current_time':current_datetime.strftime('%I:%M:%S %p'),
        'active_branch': repo.active_branch.name
    }