"""greekart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from .import views
from django.conf import settings

urlpatterns = [
    path('admin/',include('admin_honeypot.urls',namespace='admin_honeypot')),
    path('securelogin/', admin.site.urls),  #admin ka url pass karey
    path('',views.home,name="home"),  #home page ka url pass karey isliye 'blank karey'
    path('cart/',include('carts.urls')), #cart k path diye
    path('store/',include('store.urls')), #store ka path diye 
    path('orders/',include('orders.urls')),
    path('accounts/',include('accounts.urls')), #accounts ka path diye
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)



# jitne bhi app bante hai sabki urls yaha pass karte hai isey kehte first level of mapping