from django.contrib import admin

from orders.models import Order, OrderProduct,Payment

# Register your models here.

class OrderAdmin(admin.ModelAdmin): #class OrderAdmin child class (admin module hai or modeladmin parent class)
    list_display=['order_number','full_name','phone','email','city','order_total','tax','status','is_ordered','created_at']
    list_filter=['status','is_ordered']
    list_fields=['order_number','first_name','last_name','phone','email']
    
    
    

admin.site.register(Payment)         #payment model ko admin se register karey
admin.site.register(OrderProduct)    #orderproduct ko admin se register karey
admin.site.register(Order,OrderAdmin)#order,orderadmin ko admin se register karey
