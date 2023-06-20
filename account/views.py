from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
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
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # messages.error(self.request, 'Password does not match', extra_tags='danger')
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
                print(is_cart_item_exists)
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user=user 
                        item.save()
            except Cart.DoesNotExist:
                pass
            auth.login(request,user)  
            messages.success(request, "You are Logedin successfully")
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
    return render(request,'account/dashboard.html')


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
            send_email.send()
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