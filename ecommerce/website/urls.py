from django.urls import path
from .views import *

urlpatterns = [
    # OTP
    path('send-otp/', SendOTPAPIView.as_view()),
    path('resend-otp/', ResendOTPAPIView.as_view()),

    # Auth
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),

    # Category
    path('category/', CategoryAPIView.as_view()),
    path('categories/<int:id>/', CategoryDetailAPIView.as_view()),

    # Product
    path('product/', ProAPIView.as_view()),
    path('product/<int:id>/', ProDetailAPIView.as_view()),

    # Cart
    path('cart/', CartAPIView.as_view()),
    path('cart/<int:id>/', CartItemDetailAPIView.as_view()),

    # Checkout
    path('checkout/', CheckoutAPIView.as_view()),

    # Orders
    path('orders/', OrderAPIView.as_view()),
    path('orders/<int:id>/', OrderDetailAPIView.as_view()),
    path('orders/<int:order_id>/items/', OrderItemListAPIView.as_view()),
    path('orders/<int:order_id>/items/<int:item_id>/', OrderItemDetailAPIView.as_view()),
]