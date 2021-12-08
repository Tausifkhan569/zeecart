from django.db.models import query
from carts.models import Cart, CartItem
from django.contrib.auth import tokens
from django.http import request
from accounts.models import Account,UserProfile

from accounts.forms import RegistrationForm,UserForm,UserProfileForm
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id
import requests
from orders.models import Order,OrderProduct
# import for email activation
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# Create your views here.

def register(request):                                  #func register /parameter request
    if request.method=="POST":                          #if rqst.mthd == post
        form=RegistrationForm(request.POST)             #form = rgsrtnform (requset.post)
        if form.is_valid():                             #if /condition for form valid
            first_name=form.cleaned_data['first_name']  # first name from form 
            last_name=form.cleaned_data['last_name']    #last name from form .
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split("@")[0]
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,password=password,username=username)
            user.phone_number=phone_number
            user.save()
            # create a user profile
            profile=UserProfile()
            profile.user_id=user.id
            profile.profile_picture='default/default-user.png'
            profile.save
            
            # email activation
            current_site=get_current_site(request) #website fetch karega 
            mail_subject="please activate your account" #heading message ki 
            message=render_to_string("accounts/account_verification_email.html",{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #unique id will encode
                'token':default_token_generator.make_token(user)
                
                }) #jo bhi template lege usey string me conver karega   
            to_email=email       #receiver mail
            send_mail=EmailMessage(mail_subject,message,to=[to_email]) #mail which we want to send
            send_mail.send()                            #this will send the mail
            messages.success(request,"Registration Successful") #this will notify the message susccessfull
            return redirect('/accounts/login/?command=verification&email='+email) #command and verification to send activation mail
            
            
    else:                #void is not valid else it will redirect to register page     
        form=RegistrationForm()
        
    context={
        'form':form,
    }
    return render(request,'accounts/register.html',context)
 

def login(request):               #create fun login will take one parameter named/request 
    
    if request.method=="POST":     #if request method is post
        email=request.POST['email'] #email requset .post
        password=request.POST['password']   # password=requset.post
        user=auth.authenticate(email=email,password=password) #it will authenticate the email and password 
        if user is not None:#not none means user is valid
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                   cart_item=CartItem.objects.filter(cart=cart)
                   product_variation=[] #yaha vo user jayege jo bina log in k add kare hai 
                   for item in cart_item:
                       variation=item.variations.all()      #item sare fetch karege jo variation column m hai
                       product_variation.append(list(variation)) #jo bhi variation fetch karega usey product variation me append kardege list k form m
                       cart_item=CartItem.objects.filter(user=user) #cart item filter karke fetch karege 
                       ex_var_list=[]                                   #empty var list=[]
                       id=[]                                            #identification k liye id banaye 
                       for item in cart_item:
                        existing_variation=item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                       for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()           
            except:
                pass 
            auth.login(request,user)                #if user is valid then login successfull and redirect to home page
            messages.success(request,"log in successful")
            url=request.META.get('HTTP_REFERER')
            print(f'URL:{url}')
            try:
                query=requests.utils.urlparse(url).query
                params=dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    nextPage=params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:                                  #else user enter wrong credential then receive invalid credential message
            messages.error(request,"Invalid Credentials")
            return redirect('login')              
        
    return render(request,'accounts/login.html')

@login_required(login_url='login') #redirect when user is not logged in

def logout(request):        #fun logout will take one parameter/request
    auth.logout(request)    
    messages.success(request,"you are successfully logged out")
    return redirect('login') #returns when user is logged out 

def activate(request,uidb64,token):   #fun activate which will take parameters/requset,uidb64,token
    try:
        uid=urlsafe_base64_decode(uidb64).decode() 
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,"your account has been activated ")
        return redirect('login')
    else:
        messages.error(request,"Invalid Activation link ")
        return redirect('register')

@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile=UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)

def forgotPassword(request):  #fuction forgotpassword
    if request.method=="POST":   #agr requset method post hai to
        email=request.POST['email'] #isse email post hoga database me 
        if Account.objects.filter(email=email).exists():    #yaha check hoga ki user ka dala hua email  hai ya nahi db me
            user=Account.objects.get(email__exact=email)    #agr db m email hai to get(email__exact=email) compare hoga email 
            
            current_site=get_current_site(request) #website fetch karega 
            mail_subject="Reset Your Password" #heading message ki 
            message=render_to_string("accounts/reset_password_email.html",{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), #unique id will encode
                'token':default_token_generator.make_token(user)
                
                }) #jo bhi template lege usey string me conver karega   
            to_email=email       #receiver mail
            send_mail=EmailMessage(mail_subject,message,to=[to_email]) #mail which we want to send
            send_mail.send()                            #this will send the mail
            messages.success(request,"Password reset email have been sent on ur email addrs") #this will notify the message susccessfull
            return redirect('login') #will redirect to login page
        else:
            messages.error(request,"Account Does not Exist") #jab database me user ka dala hua email nahi rhega to ye print hoga
            return redirect('forgotPassword')               #or fir forgot password k page p redirect k
    return render(request,'accounts/forgotPassword.html')
            

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,"Please reset Your Password")
        return redirect('resetPassword')
    

def resetPassword(request):
    if request.method=="POST":
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password == confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset has been sucessfull")
            return redirect('login')
        else:
            messages.error(request,"password does not match")
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile =get_object_or_404(UserProfile,user=request.user)
    # userprofile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)

