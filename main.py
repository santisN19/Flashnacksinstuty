import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flashnacks.settings')
    
    try:
        # Agregar el directorio actual al path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        
        django.setup()
        print("✅ Django inicializado correctamente")
        print("🚀 Iniciando servidor en http://127.0.0.1:8000/")
        
        # Crear argumentos COMPLETOS para execute_from_command_line
        args = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']
        execute_from_command_line(args)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")