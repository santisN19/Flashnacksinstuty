from django.http import HttpResponse
from django.shortcuts import render
from .models import Producto

# Vista principal (para la raíz del sitio)
def home(request):
    return HttpResponse("¡Hola, FlashNacks está en línea!")

# Vista del cliente (general)
def cliente_view(request):
    return render(request, "core/cliente.html")

# Vista de menú filtrado por negocio
def menu_negocio_view(request, negocio):
    # Filtra productos según el proveedor (negocio)
    productos = Producto.objects.filter(inventario__proveedor__iexact=negocio)
    return render(request, "core/cliente.html", {
        "negocio": negocio,
        "productos": productos
    })
