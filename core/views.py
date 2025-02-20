from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetSerializer,
    UserProfileSerializer,
    OrderSerializer,
)

User = get_user_model()

@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(["POST"])
def password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        user = get_object_or_404(User, email=email)

        reset_link = f"{settings.FRONTEND_URL}/reset-password?email={email}"
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response(
            {"message": "Password reset instructions have been sent to your email."},
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT"])
def profile(request):
    user = request.user

    if request.method == "GET":
        orders = Order.objects.filter(user=user)
        user_serializer = UserProfileSerializer(user)
        order_serializer = OrderSerializer(orders, many=True)  # Serialize orders with items

        return Response({
            "user": user_serializer.data,
            "orders": order_serializer.data,  # Include order details with items
        })

    elif request.method == "PUT":
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully.", "user": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

