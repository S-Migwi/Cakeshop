from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost_price','price', 'stock', 'created_at', 'updated_at')

# Register your models here.
