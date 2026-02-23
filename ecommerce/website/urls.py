from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),

    path('category/', CategoryAPIView.as_view()),
    path('categories/<int:id>/', CategoryDetailAPIView.as_view()),

    path('product/', ProAPIView.as_view()),
    path('product/<int:id>/', ProDetailAPIView.as_view()),

    path('cart/', CartAPIView.as_view()),
    path('cart/<int:id>/', CartItemDetailAPIView.as_view()),

    path('checkout/', CheckoutAPIView.as_view()),


    path('send-otp/', SendOTPAPIView.as_view()),
    path('resend-otp/', ResendOTPAPIView.as_view()),
    path('register/', RegisterAPIView.as_view()),
    path('orders/', OrderAPIView.as_view()),           # list all orders
    path('orders/<int:id>/', OrderDetailAPIView.as_view())
    
]