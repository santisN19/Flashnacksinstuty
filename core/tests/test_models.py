from django.test import TestCase
from core.models import Producto

class ProductoModelTest(TestCase):

    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Papa criolla",
            precio=2500,
            stock_actual=10
        )

    def test_creacion_producto(self):
        """El producto se crea correctamente con los atributos dados"""
        self.assertEqual(self.producto.nombre, "Papa criolla")
        self.assertEqual(self.producto.precio, 2500)
        self.assertEqual(self.producto.stock_actual, 10)

    def test_str_producto(self):
        """El método __str__ devuelve el nombre"""
        self.assertEqual(str(self.producto), "Papa criolla")
