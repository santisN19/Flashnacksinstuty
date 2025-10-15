from django.test import TestCase
from django.urls import reverse

class ProductoViewsTest(TestCase):

    def test_index_view_status(self):
        """La vista index responde con 200"""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_contenido(self):
        """La vista index contiene texto esperado"""
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Bienvenido")
