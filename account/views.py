from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account,UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

# varification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, get_connection
from carts.views import _cart_id
from carts.models import *
from django.core.mail import send_mail
from orders.models import Order
import requests
from django.db.models import Count
from orders.models import *
# from django.contrib.auth import get_user_model
# Account=get_user_model()
# Create your views here.

def register(request):
    if request.method=="POST":
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            email=form.cleaned_data["email"]
            phone_number=form.cleaned_data["phone_number"]
            password=form.cleaned_data["password"]
            username=email.split('@')[0]
            user=Account.objects.create_user(first_name=first_name,last_name=last_name, username=username ,email=email, password=password)
            user.phone_number=phone_number
            user.save()
            user_profile = UserProfile.objects.create(user=user)
            # USER ACTIVATION
            current_site=get_current_site(request)
            mail_subject='Please activate your account'
            message=render_to_string('account/account_verification_email.html',
            {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),

            })
            from_email = 'abhaymishraspn77@gmail.com'
            recipient_list = [email]
            send_mail(mail_subject, message, from_email, recipient_list, fail_silently=False)
            # to_email=email
            # send_email=EmailMessage(mail_subject,message,to=[to_email])
            # send_email.send()
           
            messages.error(request, 'Password does not match', extra_tags='danger')
            return redirect('/account/login/?command=verification&email='+email)
            
    form=RegistrationForm()
    context={
        'form':form
    }
    return render(request,'account/register.html',context)


def login(request):
    if request.method=="POST":
        email=request.POST["email"]
        password=request.POST["password"]
       
        
        user=auth.authenticate(email=email,password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user=user 
                        item.save()
            except Cart.DoesNotExist:
                pass
            auth.login(request,user)  
            url=request.META.get('HTTP_REFERER')
            
            try:
                query=requests.utils.urlparse(url).query
                print("query->",query)
                # next=/cart/chechout/
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextpage=params['next']
                    return redirect(nextpage)
            except:
                messages.success(request, "You are Logged in successfully")
                return redirect('dashboard')
        else:
            messages.error(request, 'email or password not match', extra_tags='danger')
            return redirect('login')
    return render(request,'account/login.html')
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are Logedout successfully")
    return redirect('login')

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request, "Congratulation! Your account is actived now ")
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation Link', extra_tags='danger')
        return redirect('register')
@login_required(login_url='login')
def dashboard(request):
    orders=Order.objects.order_by('-created_at').filter(user=request.user,is_ordered=True)
    order_count=orders.count()
    userprofile = None
    try:
        userprofile=UserProfile.objects.get(user_id=request.user.id)
        print(userprofile)
    except:
        pass 
    context={
        'order_count':order_count,
        'userprofile':userprofile
    }
    return render(request,'account/dashboard.html',context)


def forgetpassword(request):
    if request.method=="POST":
        email=request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email)
            #reset password mail
            current_site=get_current_site(request)
            mail_subject='Reset Your Password'
            message=render_to_string('account/reset_verify.html',
            {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),

            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            # send_email.send()
            messages.success(request, "Password reset email has been sent to your this "+email+" email address")
            # messages.error(self.request, 'Password does not match', extra_tags='danger')
            return redirect('login')

        else:
            messages.error(request, 'This email is not registerd', extra_tags='danger')
            return redirect('forgetpassword')           
    return render(request,'account/forgetpassword.html')


def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request, "Please reset Your password")
        return redirect('resetpassword')    
    else:
        messages.error(request, 'This link has been expired!', extra_tags='danger')
        return redirect('login')

def resetpassword(request):
    if request.method=="POST":
        password=request.POST["password"]
        confirm_password=request.POST["confirm_password"]

        if password==confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "password reset successful")
            return redirect('login') 
        else:
            messages.error(request, 'Password does not match!', extra_tags='danger')  
            return redirect('resetpassword')
    else:          
        return render(request,'account/resetpassword.html')
@login_required(login_url='login')   
def my_order(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context={
        "orders":orders
    }
    return render(request,'account/my_orders.html',context)
@login_required(login_url='login')
def edit_profile(request):

    userprofile=get_object_or_404(UserProfile,user=request.user)
 
    # print("user profile:-",userprofile)
    if request.method=="POST":
        user_form=UserForm(request.POST,instance=request.user)
        profile_forms=UserProfileForm(request.POST,request.FILES,instance=userprofile)
        print(profile_forms)
        if user_form.is_valid() and profile_forms.is_valid():
            user_form.save()
            profile_forms.save()
            messages.success(request, "Your profile Updated.")   
            return redirect('edit_profile')
    else:
        user_form=UserForm(instance=request.user)
        profile_forms=UserProfileForm(instance=userprofile)
    context={
        'user_form':user_form,
        'profile_forms':profile_forms,
        'userprofile':userprofile
    }
    return render(request,'account/edit_profile.html',context)
@login_required(login_url='login')
def change_password(request):
    if request.method=="POST":
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        conform_password=request.POST['conform_password']
        user=Account.objects.get(username__exact=request.user.username)
        if new_password==conform_password:
            success=user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request,'Password update successfully please Log in!')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password!', extra_tags='danger')
        else:
            messages.error(request, 'Password does not Matched !', extra_tags='danger')
            return redirect('change_password')
    return render(request,'account/change_password.html')  

@login_required(login_url='login')
def order_detail(request,order_id):
    order_details=OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    subtotal=0
    for i in order_details:
        subtotal+=i.product_price*i.quantity
    context={
        'order_details':order_details,
        'order':order,
        'subtotal':subtotal
    }
    return render(request,'account/order_detail.html',context)