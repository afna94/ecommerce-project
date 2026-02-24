from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, pro, Order, Cart, CartItem, OrderItem
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


# --- OTP ---
class SendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=200)
        return Response(serializer.errors, status=400)


class ResendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=200)
        return Response(serializer.errors, status=400)


# --- AUTH ---
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User Registered Successfully"}, status=201)
        return Response(serializer.errors, status=400)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Invalid Credentials"}, status=400)


# --- CATEGORY ---
class CategoryAPIView(APIView):

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class CategoryDetailAPIView(APIView):

    def get(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)
        category.delete()
        return Response({"message": "Category deleted successfully"}, status=204)


# --- PRODUCT ---
class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProAPIView(APIView):

    def get(self, request):
        search = request.query_params.get('search')
        products = pro.objects.all()
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        paginator = ProductPagination()
        result = paginator.paginate_queryset(products, request)
        serializer = ProSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class ProDetailAPIView(APIView):

    def put(self, request, id):
        try:
            product = pro.objects.get(id=id)
        except pro.DoesNotExist:
            return Response({"error": "Not Found"}, status=404)
        serializer = ProSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, id):
        try:
            product = pro.objects.get(id=id)
        except pro.DoesNotExist:
            return Response({"error": "Not Found"}, status=404)
        product.delete()
        return Response({"message": "Deleted Successfully"})


# --- CART ---
class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))
        if quantity < 1:
            return Response({"error": "Quantity must be at least 1"}, status=400)
        try:
            product = pro.objects.get(id=product_id)
        except pro.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        if product.stock < quantity:
            return Response({"error": "Not enough stock"}, status=400)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared"})


class CartItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            item = CartItem.objects.get(id=id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)
        quantity = int(request.data.get("quantity", 1))
        if quantity < 1:
            return Response({"error": "Quantity must be at least 1"}, status=400)
        if quantity > item.product.stock:
            return Response({"error": "Not enough stock"}, status=400)
        item.quantity = quantity
        item.save()
        serializer = CartItemSerializer(item)
        return Response(serializer.data)

    def delete(self, request, id):
        try:
            item = CartItem.objects.get(id=id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)
        item.delete()
        return Response({"message": "Item removed from cart"})


# --- CHECKOUT ---
class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart is empty"}, status=400)
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)
        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response(
                    {"error": f"Not enough stock for {item.product.name}"},
                    status=400
                )
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()
        cart_items.delete()
        return Response({"message": "Order placed successfully", "order_id": order.id})


# --- ORDER ---
class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        order = Order.objects.create(user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            order = Order.objects.get(id=id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def delete(self, request, id):
        try:
            order = Order.objects.get(id=id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        order.delete()
        return Response({"message": "Order deleted"}, status=204)


# --- ORDER ITEMS ---
class OrderItemListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))
        try:
            product = pro.objects.get(id=product_id)
        except pro.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        if product.stock < quantity:
            return Response({"error": "Not enough stock"}, status=400)
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )
        product.stock -= quantity
        product.save()
        serializer = OrderItemSerializer(item)
        return Response(serializer.data, status=201)


class OrderItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, order_id, item_id):
        try:
            item = OrderItem.objects.get(
                id=item_id,
                order__id=order_id,
                order__user=request.user
            )
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found"}, status=404)
        serializer = OrderItemSerializer(item)
        return Response(serializer.data)

    def put(self, request, order_id, item_id):
        try:
            item = OrderItem.objects.get(
                id=item_id,
                order__id=order_id,
                order__user=request.user
            )
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found"}, status=404)

        quantity = int(request.data.get("quantity", 1))

        if quantity < 1:
            return Response({"error": "Quantity must be at least 1"}, status=400)

        available_stock = item.product.stock + item.quantity

        if quantity > available_stock:
            return Response({"error": "Not enough stock"}, status=400)

        item.product.stock = available_stock - quantity
        item.product.save()

        item.quantity = quantity
        item.price = item.product.price
        item.save()

        serializer = OrderItemSerializer(item)
        return Response(serializer.data)

    def delete(self, request, order_id, item_id):
        try:
            item = OrderItem.objects.get(
                id=item_id,
                order__id=order_id,
                order__user=request.user
            )
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found"}, status=404)
        item.delete()
        return Response({"message": "Item removed from order"})