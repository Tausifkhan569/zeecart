from django.shortcuts import render  #render isliye import karey takey html template ho kar sake
from store.models import Product  #import karey product ko jo store k models m hai 
def home(request):                         #greekart k home p jo dikhega vo hai home page 
    products=Product.objects.all().filter(is_available=True)  #sare available product product table se filter karke prodcut naam k variable ma store krdiye
    products_count=products.count()   #or fir  .count func lagake product_count var m save krdiye jisse jtne bhi product fetch karega count hoge ayega 
    context={                                 #fir context me dictionary banake patak diye
        'products':products,
        'products_count':products_count
    }
    return render(request,'home.html',context)  #or yaha context processor pass krdiye
