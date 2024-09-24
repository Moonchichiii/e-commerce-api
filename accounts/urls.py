from django.urls import path
from .views import CustomLoginView, CustomRegistrationView, CustomLogoutView, GoogleLogin, FacebookLogin,CustomPasswordResetView, CustomPasswordResetConfirmView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('register/', CustomRegistrationView.as_view(), name='custom_registration'),
    path('logout/', CustomLogoutView.as_view(), name='custom_logout'),
    path('google/login/', GoogleLogin.as_view(), name='google_login'),
    path('facebook/login/', FacebookLogin.as_view(), name='facebook_login'),
]
