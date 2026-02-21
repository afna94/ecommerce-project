from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class pro(models.Model):   
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField()

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(pro, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
