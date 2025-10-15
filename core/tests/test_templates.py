from django.test import TestCase
from django.urls import reverse

class ProductoTemplateTest(TestCase):

    def test_template_index(self):
        """La vista index usa el template correcto"""
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "index.html")  # ← CORREGIDO
        self.assertContains(response, "Bienvenido")