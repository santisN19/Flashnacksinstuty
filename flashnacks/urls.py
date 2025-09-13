from django.contrib import admin
from django.urls import path, include
from core import views  # para usar la vista home

urlpatterns = [
    path("admin/", admin.site.urls),          # Panel de administración
    path("", views.home, name="home"),        # Página principal
    path("", include("core.urls")),           # Incluye las rutas de core
]
