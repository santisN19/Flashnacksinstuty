from django.db import models
from django.contrib.auth.models import User

# ============================
# USUARIO Y CLIENTE
# ============================
class Usuario(models.Model):
    ROLES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    ]
    nombre_usuario = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_usuario


class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.nombre


# ============================
# REPARTIDOR
# ============================
class Repartidor(models.Model):
    ESTADO = [
        ('disponible', 'Disponible'),
        ('ocupado', 'Ocupado'),
    ]
    nombre = models.CharField(max_length=100)
    vehiculo = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=15, choices=ESTADO, default='disponible')

    def __str__(self):
        return self.nombre


# ============================
# INVENTARIO (AHORA VINCULADO A INGREDIENTES)
# ============================
class Inventario(models.Model):
    ingrediente = models.OneToOneField('Ingrediente', on_delete=models.CASCADE)
    cantidad_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    proveedor = models.CharField(max_length=100, blank=True, null=True)
    fecha_caducidad = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Inventario de {self.ingrediente.nombre}"

    @property
    def necesita_reabastecer(self):
        return self.cantidad_actual <= self.stock_minimo


# ============================
# INGREDIENTES (AHORA CON INVENTARIO)
# ============================
class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=20)  # ej: unidades, gramos, ml
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @property
    def stock_actual(self):
        try:
            return self.inventario.cantidad_actual
        except Inventario.DoesNotExist:
            return 0

    @property
    def stock_minimo(self):
        try:
            return self.inventario.stock_minimo
        except Inventario.DoesNotExist:
            return 0


# ============================
# PRODUCTOS (SIN RELACIÓN DIRECTA CON INVENTARIO)
# ============================
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    
    # ⭐ NUEVOS CAMPOS PARA RESTAURANTES VIRTUALES ⭐
    restaurante = models.ForeignKey(
        'RestauranteVirtual', 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    categoria_menu = models.ForeignKey(
        'CategoriaMenu', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @property
    def disponible(self):
        """Verifica si hay suficiente stock de todos los ingredientes"""
        for receta in self.receta_set.all():
            if receta.ingrediente.stock_actual < receta.cantidad_necesaria:
                return False
        return True

    @property
    def costo_produccion(self):
        """Calcula el costo basado en los ingredientes"""
        costo_total = 0
        for receta in self.receta_set.all():
            costo_total += receta.cantidad_necesaria * receta.ingrediente.costo_unitario
        return costo_total


# ============================
# RECETA (RELACIÓN PRODUCTO-INGREDIENTE)
# ============================
class Receta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad_necesaria = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['producto', 'ingrediente']

    def __str__(self):
        return f"{self.cantidad_necesaria} {self.ingrediente.unidad_medida} de {self.ingrediente.nombre} para {self.producto.nombre}"


# ============================
# MENU
# ============================
class Menu(models.Model):
    ESTADO = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    nombre = models.CharField(max_length=100)
    fecha_publicacion = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO, default='activo')
    productos = models.ManyToManyField(Producto, through='MenuProducto')

    def __str__(self):
        return self.nombre


class MenuProducto(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)


# ============================
# CARRITO TEMPORAL (ACTUALIZADO)
# ============================
class Carrito(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        if self.cliente:
            return f"Carrito de {self.cliente.nombre}"
        return f"Carrito (Session: {self.session_key})"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.detalles.all())
    
    @property
    def cantidad_total(self):
        return sum(item.cantidad for item in self.detalles.all())


class CarritoDetalle(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['carrito', 'producto']
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


# ============================
# PEDIDOS
# ============================
class Pedido(models.Model):
    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('preparacion', 'En preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]
    CANAL = [
        ('Rappi', 'Rappi'),
        ('Web', 'Web'),
        ('Telefono', 'Teléfono'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    repartidor = models.ForeignKey(Repartidor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=ESTADO, default='pendiente')
    canal = models.CharField(max_length=10, choices=CANAL)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.nombre}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


# ============================
# RESTAURANTES VIRTUALES (KFC, MCDONALD'S, ETC.)
# ============================
class RestauranteVirtual(models.Model):
    nombre = models.CharField(max_length=100)  # KFC, McDonald's, Burger King, etc.
    descripcion = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to="restaurantes/", blank=True, null=True)
    color_principal = models.CharField(max_length=7, default="#FF0000")  # Código HEX
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Restaurante Virtual"
        verbose_name_plural = "Restaurantes Virtuales"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


# ============================
# CATEGORÍAS DE MENÚ POR RESTAURANTE
# ============================
class CategoriaMenu(models.Model):
    restaurante = models.ForeignKey(RestauranteVirtual, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)  # Combos, Hamburguesas, Pollo, etc.
    descripcion = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, default='🍔')
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Categoría Menú"
        verbose_name_plural = "Categorías Menú"
        ordering = ['restaurante', 'orden', 'nombre']
    
    def __str__(self):
        return f"{self.restaurante.nombre} - {self.nombre}"


# ============================
# COMPRAS AGRUPADAS (NUEVO)
# ============================
class Compra(models.Model):
    ESTADO_COMPRA = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=15, choices=ESTADO_COMPRA, default='completada')
    
    class Meta:
        verbose_name = "Compra Agrupada"
        verbose_name_plural = "Compras Agrupadas"
        ordering = ['-fecha_compra']
    
    def __str__(self):
        return f"Compra #{self.id} - {self.usuario.nombre_usuario} - ${self.total}"

class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Item de Compra"
        verbose_name_plural = "Items de Compra"
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario