from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),   # Panel admin
    path("", include("core.urls")),  # ← TODAS las URLs de core en la raíz
]