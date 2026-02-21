from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),

    path('category/', CategoryAPIView.as_view()),

    path('product/', ProAPIView.as_view()),
    path('product/<int:id>/', ProDetailAPIView.as_view()),

    path('order/', OrderAPIView.as_view()),
]