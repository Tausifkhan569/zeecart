from .models import Cart,CartItem
from .views import _cart_id

def counter(request):
    cart_count=0
    if 'admin' in request.path:
        return{}
    else:
        try:
            cart=Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated: #jab user login karega or cart m add karta hai 
                cart_items=CartItem.objects.all().filter(user=request.user)
            else: #jab user bina log in k  cart me add karega 
                cart_items=CartItem.objects.all().filter(cart=cart[:1]) 
            for cart_item in cart_items:
                cart_count=cart_count+cart_item.quantity
        except Cart.DoesNotExist:
            cart_count=0
        return dict(cart_count=cart_count)