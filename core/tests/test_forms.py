from django.test import TestCase
from core.forms import ProductoForm

class ProductoFormTest(TestCase):

    def test_form_valido(self):
        """Formulario válido con datos correctos"""
        form_data = {"nombre": "Tomate", "precio": 1200, "cantidad": 5}
        form = ProductoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        """Formulario inválido sin precio"""
        form_data = {"nombre": "Tomate", "cantidad": 5}
        form = ProductoForm(data=form_data)
        self.assertFalse(form.is_valid())
