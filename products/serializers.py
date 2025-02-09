from rest_framework import serializers
from .models import Product,Cart,CartItem

class RelatedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image", "description", "category", "price"]

class ProductSerializer(serializers.ModelSerializer):
    related_products = serializers.SerializerMethodField()  # Add related products field
    class Meta:
        model = Product
        fields = ["id","name","slug","image","description","category","price","related_products"]
    
    def get_related_products(self, obj):
        related_products = obj.get_related_products()
        return RelatedProductSerializer(related_products, many=True).data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id", "cart_code", "created_at", "modified_at"]

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Serialize the product details
    cart = serializers.PrimaryKeyRelatedField(read_only=True)  # Serialize only the cart ID

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "product", "cart"]