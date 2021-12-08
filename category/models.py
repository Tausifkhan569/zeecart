from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):    #category class hai models module hai or Model parent class to Model k sare featurs class category use kr skti hai
    category_name=models.CharField(max_length=255,unique=True,default="") #column categoryname jo charfiled lega or unique rhega 
    slug=models.SlugField(max_length=255,unique=True)               #col slug jo slug field lega or unique ,maxlngth ktna bhi de skte
    description=models.TextField(max_length=255,blank=True)        #col desc /models. textfield or blank bhi raha to chalega
    cat_image=models.ImageField(upload_to='photos/categories',blank=True) #cat image models. image field/upld to=loc dedege ek 
    class Meta:                                  #meta ek object hai
        verbose_name="Category"                  #verbose_name = category ko plural kareg categories me 
        verbose_name_plural="Categories"
    
    def get_url(self):         
        return reverse('products_by_category',args=[self.slug])
    
    
    def __str__(self):
        return self.category_name 
    


#models .py me ham jo bhi banate hai vo backend me admin me jata hai 