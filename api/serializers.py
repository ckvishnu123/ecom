from rest_framework import serializers
from api.models import Products, Cart, Reviews

class CartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    product = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)
    created_date = serializers.CharField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "product",
            "user",
            "created_date"
        ]
    
    def create(self, validated_data):
        user = self.context.get("user")
        product = self.context.get("product")
        return product.cart_set.create(**validated_data, user=user)


class ReviewSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    product = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)
    class Meta:
        model = Reviews 
        fields = "__all__"

    def create(self, validated_data):
        product = self.context.get("product")
        user = self.context.get("user")
        return product.reviews_set.create(**validated_data, user=user)


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    product_reviews = ReviewSerializer(read_only=True, many=True)
    average_rating = serializers.CharField(read_only=True)
    class Meta:
        model = Products
        fields = "__all__"
        """ [
            "name",
            "description",
            "brand",
            "price",
            "image",
            "category"
        ] """