from django.contrib import admin
from django.urls import path
from core import views  # importa tu app principal

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),  # esta será la página principal
]
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),  # incluye las rutas de core
]
