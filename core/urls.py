from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Página principal
    path("cliente/", views.cliente_view, name="cliente"),  # Vista general de cliente
    path("cliente/<str:negocio>/", views.menu_negocio_view, name="menu_negocio"),  # Vista de negocio
]
