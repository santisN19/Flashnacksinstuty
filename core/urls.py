from django.urls import path
from . import views

urlpatterns = [
    path("cliente/", views.cliente_view, name="cliente"),
    path("cliente/<str:negocio>/", views.menu_negocio_view, name="menu_negocio"),
]
