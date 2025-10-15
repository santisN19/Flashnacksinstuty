import os
import sys
import webbrowser
from waitress import serve

# Añadir el directorio actual al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configurar la variable de entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flashnacks.settings')

# Importar la aplicación WSGI de Django
try:
    from flashnacks.wsgi import application
    print("✅ Aplicación Django cargada correctamente")
except ImportError as e:
    print(f"❌ Error importando la aplicación: {e}")
    sys.exit(1)

def main():
    print("=" * 50)
    print("🚀 INICIANDO FLASHNACKS - SOFTWARE DE ESCRITORIO")
    print("=" * 50)
    print("📊 Aplicación: Flashnacks")
    print("🌐 Servidor: http://localhost:8000")
    print("🛑 Para cerrar: Presiona Ctrl+C en esta ventana")
    print("=" * 50)
    
    # Abrir navegador automáticamente después de 2 segundos
    def abrir_navegador():
        webbrowser.open('http://localhost:8000')
    
    import threading
    timer = threading.Timer(2.0, abrir_navegador)
    timer.start()
    
    # Iniciar servidor
    try:
        serve(application, host='127.0.0.1', port=8000)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == '__main__':
    main()