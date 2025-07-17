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
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from customers import views
from customers.views import place_order, view_order, profit_loss, orders_report, delete_order, edit_order

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
    path('orders/<int:pk>/', views.view_order, name='view_order'),
    path('orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('order/edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('contact_list/', views.contact_list, name="feedback"),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('gallery/', views.product_gallery, name='product_gallery'),
    path('suppliers/', views.suppliers_page, name='suppliers_page'),
    path('supplier/delete/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),
    path('supplier/edit/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('contacts/<int:pk>/edit/', views.edit_contact, name='edit_contact'),
    path('contacts/<int:pk>/delete/', views.delete_contact, name='delete_contact'),
    path('orders/profit-loss/', views.profit_loss, name='profit_loss'),
    path('orders/orders-report/', views.orders_report, name='orders_report'),
    path('orders/report/pdf/',views.orders_report_pdf,name='orders_report_pdf'),
    path('orders/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done')
        ),
        name='password_reset'
    ),
    # Step 1 done: confirmation page
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # Step 2: link in email (enter new password)
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),

    # Step 3: reset complete
    path(
        'reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
