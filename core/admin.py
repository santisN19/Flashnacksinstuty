from django.contrib import admin
from .models import (
    Usuario, Cliente, Repartidor,
    Inventario, Producto, Ingrediente, ProductoIngrediente,
    Menu, MenuProducto,
    Carrito, CarritoDetalle,
    Pedido, DetallePedido
)


# ============================
# CONFIGURACIONES PERSONALIZADAS
# ============================

class ProductoIngredienteInline(admin.TabularInline):
    model = ProductoIngrediente
    extra = 1


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock_actual', 'stock_minimo')
    search_fields = ('nombre',)
    inlines = [ProductoIngredienteInline]


class CarritoDetalleInline(admin.TabularInline):
    model = CarritoDetalle
    extra = 1


class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha')
    inlines = [CarritoDetalleInline]


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1


class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'total', 'fecha_hora')
    list_filter = ('estado', 'canal')
    search_fields = ('cliente__nombre',)
    inlines = [DetallePedidoInline]


# ============================
# REGISTROS
# ============================

admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Repartidor)
admin.site.register(Inventario)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Ingrediente)
admin.site.register(Menu)
admin.site.register(MenuProducto)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(Pedido, PedidoAdmin)
