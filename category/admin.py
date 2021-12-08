from django.contrib import admin
from .models import Category

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):             #ek class banaye categoryadmin admin module hai or model admin parent class
    prepopulated_fields={'slug':('category_name',)} #admin me slug category k naam m slug banane prepopulated fld banaye
    list_display=('category_name','slug')          #admin me  category ka naam or slug dikhe isliye list display banaye
admin.site.register(Category,CategoryAdmin)   #admin ko register krdiye or jtne bhi class hai category k or admin k sb
