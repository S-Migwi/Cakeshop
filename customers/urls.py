"""
URL configuration for cakeShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from tkinter.font import names

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from customers import views
from customers.views import place_order, view_order

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index,name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/edit/<int:pk>/', views.product_update, name='product_update'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('orders/', place_order, name='place_order'),
    path('orders/<int:pk>/', view_order, name='view_order'),
    path('orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('order/edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('contact_list/', views.contact_list, name="feedback"),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('gallery/', views.product_gallery, name='product_gallery'),
    path('suppliers/', views.suppliers_page, name='suppliers_page'),

]
