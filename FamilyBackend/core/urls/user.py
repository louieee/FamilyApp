from django.urls import path
from rest_framework.routers import SimpleRouter

from ..views import user

app_name = "user"
router = SimpleRouter()
router.register("roles", user.RoleAPI)

urlpatterns = [
	path("auth/login", user.LoginAPI.as_view(), name="auth-login"),
	path("", user.UserAPI.as_view(), name="logged-in-user"),
	path("auth/reset-password/<str:hash_code>/", user.ResetPasswordAPI.as_view(), name="reset-password"),
	path("auth/forgot-password", user.ForgotPasswordAPI.as_view(), name="forgot-password"),
	path("change-password", user.ChangePasswordAPI.as_view(), name="change-password")
]
urlpatterns.extend(router.urls)
