from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, pro, Order
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User Registered Successfully"})
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



class ProductPagination(PageNumberPagination):
    page_size = 5


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



class OrderAPIView(APIView):

    def post(self, request):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity"))

        product = pro.objects.get(id=product_id)

        total = product.price * quantity

        Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=total
        )

        return Response({"message": "Order Placed Successfully"})        