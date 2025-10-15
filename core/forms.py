from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "precio", "descripcion", "imagen"]  # ajusta si tu modelo tiene más campos
