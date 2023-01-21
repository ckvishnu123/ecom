from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Products(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, null=True)
    brand = models.CharField(max_length=30)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to="images", null=True)
    category = models.CharField(max_length=30)

    @property
    def average_rating(self):
        ratings = self.reviews_set.all().values_list("rating", flat=True)
        if ratings:
            return sum(ratings)/len(ratings)
        else:
            return 0

    @property
    def product_reviews(self):
        return self.reviews_set.all()

    def __str__(self):
        return self.name


class Reviews(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=30)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product


class Cart(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    # ("value send to backend" - "field name")
    options = (
        ("in-cart", "in-cart"),
        ("order-placed", "order-placed"),
        ("removed", "removed")
    )
    status = models.CharField(max_length=30, choices=options, default="in-cart")

    def __str__(self):
        return self.product