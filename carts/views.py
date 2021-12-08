from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.
def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def add_cart(request,product_id):
    current_user=request.user    #column ka naam user hai isliye .user use karey
    product=Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation=[]
    
        if request.method == 'POST':
            for item in request.POST:
                key=item
                value=request.POST.get(key)
                print(key,value)

                try:

                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    print(variation)
                    product_variation.append(variation)
                
                except:
                    pass
        is_cart_item_exists=CartItem.objects.filter(product=product,user=current_user).exists() #variable banaye iscartitemexist cart item hai ya nahii isliye filter karey 
        if is_cart_item_exists:   #agar cart item exis karta hai to
            cart_item=CartItem.objects.filter(user=current_user,product=product) #cart item filter karke fetch karege 
            ex_var_list=[]                         #empty var list=[]
            id=[]                                  #fetch karne ke liya id use karte hai  
            for item in cart_item:                 #item iterator hai 
                existing_variation=item.variations.all()  #jitne bhi add hai sare variation layega 
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            else:
                item=CartItem.objects.create(product=product,quantity=1,user=current_user)
                if len(product_variation)>0:
                    item.variations.clear()
                # for item in product_variation:
                item.variations.add(*product_variation)
            #cart_item.quantity+=1
                item.save()
        else:
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                # for item in product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

    else:
        # product=Product.objects.get(id=product_id)
        product_variation=[]
    
        if request.method == 'POST':
            for item in request.POST:
                key=item
                value=request.POST[key]
                print(key,value)

                try:

                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    print(variation)
                    product_variation.append(variation)
                
                except:
                    pass
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart=Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        is_cart_item_exists=CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item=CartItem.objects.filter(cart=cart,product=product)
            ex_var_list=[]
            id=[]   #fetch karne ke liya id use karte hai  
            for item in cart_item:
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
                
            else:
                item=CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    item.save()
        else:
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                # for item in product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')


         
def remove_cart(request,product_id,cart_item_id): #func remove cart 4 paramtr lega rqst,product_id,cart_item_id
    product=get_object_or_404(Product,id=product_id) #sabse pehla product fetch hoga product table se id k base p 
    try: 
        if request.user.is_authenticated:           #agr user authenticatd hai 
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
            #aagr user authenticatd hai to user ka cart_item fetch karege product/user/id se 
        else:
            #else agr user authenticate nahi hai to  cart_id k base pe cart or cart_item fetch hoga 
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)   
        if cart_item.quantity>1:     #if cart_item ki quantity 1 se zyada hai to remove button work karega 
                cart_item.quantity=cart_item.quantity-1  #minus cart_item quantity
                cart_item.save()              #minus karke save 
        else:
                cart_item.delete()     #else 1 hi item hai to cartitem  delete  
    except:
        pass
    return redirect('cart')   #redirect to cart page

def remove_cart_item(request,product_id,cart_item_id):
    #function removecartitem jo remove button pe click karke pura cartitem delete hojayega 
    product=get_object_or_404(Product,id=product_id) #product fetch hoga agr nahi hua to errror 404 
    try:
        if request.user.is_authenticated:      #if request authenticated hai to uska cart item fetch hoga user/cart id 
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else: #else _cart_id k base p cart item fetch kreke delete krdega
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)  
    except:
        pass 
    cart_item.delete()
    return redirect('cart')
    

def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
    
        for cart_item in cart_items:
            total=total+(cart_item.product.price*cart_item.quantity)
            quantity=quantity+cart_item.quantity
            tax=(8*total)/100
            grand_total=total+tax
        
    except ObjectDoesNotExist:
        pass    
        
    context={
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request,'store/cart.html',context)

@login_required(login_url="login")
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
    
        for cart_item in cart_items:
            total=total+(cart_item.product.price*cart_item.quantity)
            quantity=quantity+cart_item.quantity
            tax=(8*total)/100
            grand_total=total+tax
        
    except ObjectDoesNotExist:
        pass    
        
    context={
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request,'store/checkout.html',context)