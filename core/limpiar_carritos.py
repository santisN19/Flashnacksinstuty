import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flashnacks.settings')
django.setup()

from core.models import Carrito, Cliente

def limpiar_carritos_duplicados():
    """Limpia carritos duplicados activos para cada cliente"""
    clientes = Cliente.objects.all()
    
    for cliente in clientes:
        carritos_activos = Carrito.objects.filter(cliente=cliente, activo=True)
        
        if carritos_activos.count() > 1:
            print(f"Cliente: {cliente.nombre} - Carritos activos: {carritos_activos.count()}")
            
            # Mantener el carrito más reciente
            carrito_mantener = carritos_activos.order_by('-fecha_creacion').first()
            
            # Desactivar los demás
            carritos_desactivar = carritos_activos.exclude(id=carrito_mantener.id)
            carritos_desactivar.update(activo=False)
            
            print(f"  Mantenido: {carrito_mantener.id}")
            print(f"  Desactivados: {[c.id for c in carritos_desactivar]}")
    
    print("Limpieza completada!")

if __name__ == "__main__":
    limpiar_carritos_duplicados()