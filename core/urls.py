from django.urls import path
from .views import RegisterView, LoginView, PasswordResetView, ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
]