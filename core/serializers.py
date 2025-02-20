# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Order,OrderItem
from products.serializers import ProductSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'city', 'state', 'address', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','name', 'city', 'state', 'address', 'phone']
        read_only_fields = ['id', 'username'] 

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('name', instance.username)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save()
        return instance

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer() 

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True) 

    class Meta:
        model = Order
        fields = ["id", "user", "total_price", "created_at", "items"]