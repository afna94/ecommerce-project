from django.contrib import admin
from .models import Category, pro, Cart, CartItem, Order, OrderItem

admin.site.register(Category)
admin.site.register(pro)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)