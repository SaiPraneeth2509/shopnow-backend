from django.urls import path
from .views import LoginView
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("password-reset/", views.password_reset, name="password_reset"),
    path("profile/", views.profile, name="profile"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]