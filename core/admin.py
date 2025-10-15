from django.contrib import admin
from .models import (
    # ============================
    # USUARIOS Y CLIENTES
    # ============================
    Usuario, Cliente,
    
    # ============================
    # REPARTIDORES Y PEDIDOS
    # ============================
    Repartidor, Pedido, DetallePedido,
    
    # ============================
    # INGREDIENTES E INVENTARIO
    # ============================
    Ingrediente, Inventario,
    
    # ============================
    # PRODUCTOS Y RECETAS
    # ============================
    Producto, Receta,
    
    # ============================
    # RESTAURANTES Y MENÚS
    # ============================
    RestauranteVirtual, CategoriaMenu, Menu, MenuProducto,
    
    # ============================
    # CARRITO Y COMPRAS
    # ============================
    Carrito, CarritoDetalle, Compra, ItemCompra
)


# ============================
# INLINES
# ============================

class RecetaInline(admin.TabularInline):
    """Ingredientes de un producto"""
    model = Receta
    extra = 1
    verbose_name = "Ingrediente necesario"
    verbose_name_plural = "Receta - Ingredientes necesarios"


class CarritoDetalleInline(admin.TabularInline):
    """Items del carrito"""
    model = CarritoDetalle
    extra = 1
    verbose_name = "Producto en carrito"
    verbose_name_plural = "Productos en carrito"


class DetallePedidoInline(admin.TabularInline):
    """Items del pedido"""
    model = DetallePedido
    extra = 1
    verbose_name = "Producto en pedido"
    verbose_name_plural = "Productos en pedido"


class ItemCompraInline(admin.TabularInline):
    """Items de la compra agrupada"""
    model = ItemCompra
    extra = 1
    verbose_name = "Producto comprado"
    verbose_name_plural = "Productos comprados"


# ============================
# ADMIN CONFIGURATIONS
# ============================

# USUARIOS Y CLIENTES
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombre_usuario', 'email', 'rol', 'fecha_registro', 'activo']
    list_filter = ['rol', 'activo', 'fecha_registro']
    search_fields = ['nombre_usuario', 'email']
    list_editable = ['activo']
    ordering = ['-fecha_registro']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario', 'telefono', 'direccion']
    search_fields = ['nombre', 'usuario__nombre_usuario']
    list_filter = ['usuario__rol']


# REPARTIDORES
@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'vehiculo', 'estado']
    list_filter = ['estado']
    search_fields = ['nombre']
    list_editable = ['estado']


# INGREDIENTES E INVENTARIO
@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'unidad_medida', 'costo_unitario', 'stock_actual', 'activo']
    list_filter = ['activo', 'unidad_medida']
    search_fields = ['nombre']
    list_editable = ['costo_unitario', 'activo']
    ordering = ['nombre']


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['ingrediente', 'cantidad_actual', 'stock_minimo', 'necesita_reabastecer', 'fecha_ultima_actualizacion']
    list_filter = []  # CORREGIDO: Removido 'necesita_reabastecer' de list_filter
    search_fields = ['ingrediente__nombre']
    list_editable = ['cantidad_actual', 'stock_minimo']
    ordering = ['ingrediente__nombre']
    
    def necesita_reabastecer(self, obj):
        return obj.necesita_reabastecer
    necesita_reabastecer.boolean = True
    necesita_reabastecer.short_description = 'Necesita Reabastecer'


# PRODUCTOS Y RECETAS
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'restaurante', 'categoria_menu', 'destacado', 'disponible', 'activo']
    list_filter = ['restaurante', 'categoria_menu', 'destacado', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'destacado', 'activo']
    inlines = [RecetaInline]
    ordering = ['restaurante', 'nombre']
    
    def disponible(self, obj):
        return obj.disponible
    disponible.boolean = True
    disponible.short_description = 'Disponible'


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'ingrediente', 'cantidad_necesaria']
    list_filter = ['producto__restaurante', 'ingrediente']
    search_fields = ['producto__nombre', 'ingrediente__nombre']
    ordering = ['producto__nombre']


# RESTAURANTES Y MENÚS
@admin.register(RestauranteVirtual)
class RestauranteVirtualAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'orden', 'color_principal']
    list_filter = ['activo']
    search_fields = ['nombre']
    list_editable = ['activo', 'orden', 'color_principal']
    ordering = ['orden', 'nombre']


@admin.register(CategoriaMenu)
class CategoriaMenuAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'restaurante', 'icono', 'orden']
    list_filter = ['restaurante']
    search_fields = ['nombre', 'restaurante__nombre']
    list_editable = ['icono', 'orden']
    ordering = ['restaurante', 'orden', 'nombre']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'fecha_publicacion']
    list_filter = ['estado']
    search_fields = ['nombre']
    list_editable = ['estado']
    # CORREGIDO: Removido filter_horizontal para 'productos' porque usa through model


@admin.register(MenuProducto)
class MenuProductoAdmin(admin.ModelAdmin):
    list_display = ['menu', 'producto']
    list_filter = ['menu', 'menu__estado']
    search_fields = ['menu__nombre', 'producto__nombre']


# CARRITO
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'session_key', 'fecha_creacion', 'cantidad_total', 'total', 'activo']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['cliente__nombre', 'session_key']
    inlines = [CarritoDetalleInline]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def cantidad_total(self, obj):
        return obj.cantidad_total
    cantidad_total.short_description = 'Total Items'
    
    def total(self, obj):
        return f"${obj.total}"
    total.short_description = 'Total'


@admin.register(CarritoDetalle)
class CarritoDetalleAdmin(admin.ModelAdmin):
    list_display = ['carrito', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['carrito__activo']
    search_fields = ['producto__nombre', 'carrito__cliente__nombre']
    
    def subtotal(self, obj):
        return f"${obj.subtotal}"
    subtotal.short_description = 'Subtotal'


# PEDIDOS
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'estado', 'canal', 'total', 'fecha_hora', 'repartidor']
    list_filter = ['estado', 'canal', 'fecha_hora']
    search_fields = ['cliente__nombre']
    inlines = [DetallePedidoInline]
    list_editable = ['estado']
    ordering = ['-fecha_hora']


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['pedido__estado']
    search_fields = ['producto__nombre', 'pedido__cliente__nombre']


# COMPRAS AGRUPADAS
@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'fecha_compra', 'total', 'estado']
    list_filter = ['estado', 'fecha_compra']
    search_fields = ['usuario__nombre_usuario']
    inlines = [ItemCompraInline]
    readonly_fields = ['fecha_compra']
    ordering = ['-fecha_compra']


@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = ['compra', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['compra__estado']
    search_fields = ['producto__nombre', 'compra__usuario__nombre_usuario']


# ============================
# CONFIGURACIÓN DEL SITIO ADMIN
# ============================
admin.site.site_header = "FlashSnacks - Administración"
admin.site.site_title = "FlashSnacks Admin"
admin.site.index_title = "Panel de Administración"