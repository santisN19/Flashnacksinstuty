from django.http import HttpResponse
from django.shortcuts import render

# Vista principal (para la raíz del sitio)
def home(request):
    return HttpResponse("¡Hola, FlashNacks está en línea!")

# Vista para el cliente
def cliente_view(request):
    return render(request, "core/cliente.html")
from django.shortcuts import render
from .models import Producto

def cliente_view(request):
    return render(request, "core/cliente.html")

def menu_negocio_view(request, negocio):
    # Filtra productos según el proveedor (negocio)
    productos = Producto.objects.filter(inventario__proveedor__iexact=negocio)
    return render(request, "core/cliente.html", {"negocio": negocio, "productos": productos})
