"""FamilyManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

swagger_view = get_schema_view(
    info=openapi.Info(
        title=f"Family App API",
        default_version=f"Version 1",
        terms_of_service="localhost:8000",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "docs/", swagger_view.with_ui("swagger", cache_timeout=0), name="swagger_docs"
    ),
    path(
        "re-docs/",
        swagger_view.with_ui("redoc", cache_timeout=0),
        name="swagger_redocs",
    ),
    path("api/", include("core.urls")),
]
