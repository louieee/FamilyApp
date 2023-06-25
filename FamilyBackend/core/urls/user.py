from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import user

app_name = "user"
router = SimpleRouter()

urlpatterns = [
	path("auth/login", user.LoginAPI.as_view(), name="auth-login"),
	path("", user.UserAPI.as_view(), name="logged-in-user"),
	path("auth/reset-password", user.ResetPasswordAPI.as_view(), name="reset-password"),
	path("auth/forgot-password", user.ForgotPasswordAPI.as_view(), name="forgot-password")
]
urlpatterns.extend(router.urls)
