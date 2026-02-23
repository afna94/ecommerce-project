from rest_framework import serializers
from .models import Category, pro, Order, Cart, CartItem, OrderItem
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return data
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProSerializer(serializers.ModelSerializer):
    class Meta:
        model = pro
        fields = '__all__'

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.FloatField(source='product.price', read_only=True)
    subtotal = serializers.FloatField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.FloatField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total', 'created_at']
        read_only_fields = ['user']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'items']
        read_only_fields = ['user']


import random
import re
from .models import OTP
from .utils import send_otp_email

# --- SEND OTP ---
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip()

    def create(self, validated_data):
        email = validated_data['email']
        otp = str(random.randint(100000, 999999))
        OTP.objects.create(identifier=email, otp=otp)
        send_otp_email(email, otp)
        return {'message': 'OTP sent to email', 'email': email}


# --- RESEND OTP ---
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data['email'].strip()
        otp = str(random.randint(100000, 999999))
        OTP.objects.create(identifier=email, otp=otp)
        send_otp_email(email, otp)
        return {'message': 'OTP resent to email', 'email': email}


# --- REGISTER WITH OTP ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    otp = serializers.CharField(write_only=True, max_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'otp']

    def validate(self, data):
        # Password match check
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )

        # OTP check
        email = data['email'].strip()
        try:
            otp_instance = OTP.objects.get(identifier=email)
        except OTP.DoesNotExist:
            raise serializers.ValidationError(
                {"otp": "No OTP found — send OTP first"}
            )

        if not otp_instance.is_valid(data['otp']):
            raise serializers.ValidationError(
                {"otp": "Invalid or expired OTP"}
            )

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('otp')
        email = validated_data['email'].strip()

        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
            password=validated_data['password']
        )

        # OTP delete after registration
        OTP.objects.filter(identifier=email).delete()

        return user        