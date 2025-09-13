from django.db import models


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
# INVENTARIO Y PRODUCTOS
# ============================
class Inventario(models.Model):
    fecha_registro = models.DateField()
    proveedor = models.CharField(max_length=100, blank=True, null=True)
    fecha_caducidad = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Inventario {self.id} - {self.proveedor}"


class Producto(models.Model):
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)

    def __str__(self):
        return self.nombre


# ============================
# INGREDIENTES
# ============================
class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100)
    unidad = models.CharField(max_length=20)  # ej: unidades, gramos, ml
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre


class ProductoIngrediente(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad_necesaria = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad_necesaria} {self.ingrediente.unidad} de {self.ingrediente.nombre} para {self.producto.nombre}"


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
# CARRITO TEMPORAL
# ============================
class Carrito(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito {self.id} de {self.cliente.nombre}"


class CarritoDetalle(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


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
