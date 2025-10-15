from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .models import Producto, RestauranteVirtual, CategoriaMenu, Carrito, CarritoDetalle, Cliente, Usuario, Compra, ItemCompra
import json

# ============================
# VISTAS PRINCIPALES
# ============================

def index(request):
    restaurantes = RestauranteVirtual.objects.filter(activo=True).order_by('orden')
    context = {
        'restaurantes': restaurantes,
    }
    return render(request, "index.html", context)

def menu_restaurante(request, restaurante_id):
    restaurante = get_object_or_404(RestauranteVirtual, id=restaurante_id, activo=True)
    categorias = CategoriaMenu.objects.filter(restaurante=restaurante).order_by('orden')
    
    # CORREGIDO: Ya no usamos stock_actual, usamos la propiedad 'disponible'
    productos = Producto.objects.filter(
        restaurante=restaurante,
        activo=True
    )
    
    # Filtrar productos destacados que estén disponibles
    productos_destacados = [p for p in productos if p.destacado and p.disponible][:6]
    
    productos_por_categoria = {}
    for categoria in categorias:
        productos_categoria = productos.filter(categoria_menu=categoria)
        # Filtrar solo los disponibles
        productos_disponibles = [p for p in productos_categoria if p.disponible]
        if productos_disponibles:
            productos_por_categoria[categoria] = productos_disponibles
    
    context = {
        'restaurante': restaurante,
        'categorias': categorias,
        'productos_destacados': productos_destacados,
        'productos_por_categoria': productos_por_categoria,
    }
    return render(request, "menu_restaurante.html", context)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # CORREGIDO: Filtrar productos relacionados que estén disponibles
    productos_relacionados = Producto.objects.filter(
        categoria_menu=producto.categoria_menu,
        activo=True
    ).exclude(id=producto.id)
    
    # Filtrar solo los disponibles
    productos_relacionados_disponibles = [p for p in productos_relacionados if p.disponible][:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados_disponibles,
    }
    return render(request, "detalle_producto.html", context)

# ============================
# VISTAS DEL CARRITO (ACTUALIZADAS)
# ============================

def obtener_o_crear_carrito(request):
    """Obtiene o crea un carrito para el usuario o sesión"""
    try:
        # Para usuarios autenticados
        if request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(nombre_usuario=request.user.username)
                cliente, created = Cliente.objects.get_or_create(
                    usuario=usuario,
                    defaults={'nombre': usuario.nombre_usuario}
                )
                
                # Buscar carrito activo existente
                carrito = Carrito.objects.filter(cliente=cliente, activo=True).first()
                if carrito:
                    return carrito
                else:
                    return Carrito.objects.create(cliente=cliente, activo=True)
                    
            except (Usuario.DoesNotExist, Cliente.DoesNotExist):
                pass
        
        # Para usuarios no autenticados - USAR SESIÓN
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        carrito = Carrito.objects.filter(session_key=session_key, activo=True).first()
        
        if carrito:
            return carrito
        else:
            return Carrito.objects.create(session_key=session_key, activo=True)
            
    except Exception as e:
        print(f"Error en obtener_o_crear_carrito: {e}")
        # Crear carrito de emergencia
        if not request.session.session_key:
            request.session.create()
        return Carrito.objects.create(session_key=request.session.session_key, activo=True)

def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito real - VERSIÓN ACTUALIZADA"""
    if request.method == 'POST':
        try:
            print(f"🔄 AGREGAR AL CARRITO - Producto ID: {producto_id}")
            
            producto = get_object_or_404(Producto, id=producto_id)
            print(f"📦 Producto encontrado: {producto.nombre}")
            
            # CORREGIDO: Usar propiedad 'disponible' en lugar de stock_actual
            if not producto.disponible:
                print("❌ Producto no disponible")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': f'❌ {producto.nombre} no está disponible'
                    })
                messages.error(request, f'❌ {producto.nombre} no está disponible')
                return redirect('core:detalle_producto', producto_id=producto_id)
            
            carrito = obtener_o_crear_carrito(request)
            print(f"🛒 Carrito obtenido: ID={carrito.id}, Cliente={carrito.cliente}, Session={carrito.session_key}")
            
            # Usar get_or_create para evitar duplicados
            item, created = CarritoDetalle.objects.get_or_create(
                carrito=carrito,
                producto=producto,
                defaults={
                    'precio_unitario': producto.precio, 
                    'cantidad': 1
                }
            )
            
            if not created:
                item.cantidad += 1
                # CORREGIDO: No podemos verificar stock exacto sin lógica más compleja
                # Por ahora permitimos agregar, pero en la compra se verificará
                item.save()
                print(f"📈 Producto actualizado: {producto.nombre} x {item.cantidad}")
            else:
                print(f"✅ Producto creado: {producto.nombre} x 1")
            
            # VERIFICAR que se guardó
            items_count = carrito.detalles.count()
            print(f"📊 Carrito ahora tiene: {items_count} items")
            
            mensaje = f'✅ {producto.nombre} agregado al carrito'
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'mensaje': mensaje,
                    'cantidad_total': carrito.cantidad_total,
                    'total': float(carrito.total)
                })
                
            messages.success(request, mensaje)
                
        except Exception as e:
            print(f"🔥 ERROR en agregar_al_carrito: {str(e)}")
            error_msg = f'Error al agregar el producto: {str(e)}'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
    
    return redirect('core:detalle_producto', producto_id=producto_id)

def ver_carrito(request):
    """Muestra el contenido del carrito"""
    carrito = obtener_o_crear_carrito(request)
    items = carrito.detalles.select_related('producto').all()
    
    context = {
        'carrito': carrito,
        'items': items,
    }
    return render(request, 'carrito.html', context)

def actualizar_carrito(request, item_id):
    """Actualiza la cantidad de un item en el carrito"""
    if request.method == 'POST':
        try:
            carrito = obtener_o_crear_carrito(request)
            item = get_object_or_404(CarritoDetalle, id=item_id, carrito=carrito)
            nueva_cantidad = int(request.POST.get('cantidad', 1))
            
            if nueva_cantidad > 0:
                # CORREGIDO: Verificar disponibilidad en lugar de stock
                # Nota: Esta verificación es básica, podrías hacerla más precisa
                if item.producto.disponible:
                    item.cantidad = nueva_cantidad
                    item.save()
                    messages.success(request, 'Carrito actualizado')
                else:
                    messages.error(request, f'{item.producto.nombre} ya no está disponible')
            else:
                item.delete()
                messages.success(request, 'Producto eliminado del carrito')
                
        except Exception as e:
            messages.error(request, 'Error al actualizar el carrito')
    
    return redirect('core:ver_carrito')

def eliminar_del_carrito(request, item_id):
    """Elimina un item del carrito"""
    if request.method == 'POST':
        try:
            carrito = obtener_o_crear_carrito(request)
            item = get_object_or_404(CarritoDetalle, id=item_id, carrito=carrito)
            producto_nombre = item.producto.nombre
            item.delete()
            messages.success(request, f'❌ {producto_nombre} eliminado del carrito')
        except Exception as e:
            messages.error(request, 'Error al eliminar el producto')
    
    return redirect('core:ver_carrito')

def limpiar_carrito(request):
    """Limpia todo el carrito"""
    if request.method == 'POST':
        try:
            carrito = obtener_o_crear_carrito(request)
            carrito.detalles.all().delete()
            messages.success(request, '🛒 Carrito vaciado')
        except Exception as e:
            messages.error(request, 'Error al limpiar el carrito')
    
    return redirect('core:ver_carrito')

# ============================
# VISTAS DE COMPRAS (ACTUALIZADAS)
# ============================

@login_required
def comprar_ahora(request):
    """Procesa la compra desde el carrito real - VERSIÓN ACTUALIZADA"""
    if request.method == 'POST':
        try:
            carrito = obtener_o_crear_carrito(request)
            items_carrito = carrito.detalles.select_related('producto').all()
            
            print(f"🛒 Carrito antes de comprar: {items_carrito.count()} items")
            
            if not items_carrito.exists():
                messages.error(request, "Tu carrito está vacío")
                return redirect('core:ver_carrito')
            
            # Obtener el usuario actual
            try:
                usuario = Usuario.objects.get(nombre_usuario=request.user.username)
            except Usuario.DoesNotExist:
                messages.error(request, "Usuario no encontrado")
                return redirect('core:ver_carrito')
            
            # Crear la compra agrupada
            compra = Compra.objects.create(
                usuario=usuario,
                total=0  # Se calculará después
            )
            
            total_compra = 0
            productos_comprados = []
            
            # Transferir items del carrito a la compra
            for item_carrito in items_carrito:
                # CORREGIDO: Verificar disponibilidad en lugar de stock
                if not item_carrito.producto.disponible:
                    messages.warning(request, f"Producto no disponible: {item_carrito.producto.nombre}")
                    continue
                
                # Crear item de compra
                item_compra = ItemCompra.objects.create(
                    compra=compra,
                    producto=item_carrito.producto,
                    cantidad=item_carrito.cantidad,
                    precio_unitario=item_carrito.precio_unitario
                )
                
                # CORREGIDO: Ya no actualizamos stock del producto directamente
                # La lógica de inventario se maneja a nivel de ingredientes
                
                total_compra += item_compra.subtotal
                productos_comprados.append(item_carrito.producto.nombre)
                
                print(f"✅ Producto comprado: {item_carrito.producto.nombre} x {item_carrito.cantidad}")
            
            # Actualizar total de la compra
            compra.total = total_compra
            compra.save()
            
            # Limpiar el carrito
            carrito.detalles.all().delete()
            
            if productos_comprados:
                messages.success(request, f"¡Compra realizada exitosamente! Productos: {', '.join(productos_comprados)} - Total: ${total_compra}")
                print(f"🎉 Compra completada: ${total_compra}")
                return redirect('core:mis_compras')
            else:
                compra.delete()
                messages.error(request, "No se pudo procesar la compra - productos no disponibles")
                return redirect('core:ver_carrito')
                
        except Exception as e:
            print(f"🔥 Error en comprar_ahora: {str(e)}")
            messages.error(request, f"Error al procesar la compra: {str(e)}")
            return redirect('core:ver_carrito')
    
    # Si no es POST, redirigir al carrito
    return redirect('core:ver_carrito')

@login_required
def mis_compras(request):
    """Muestra todas las compras agrupadas del usuario"""
    try:
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)
        compras = Compra.objects.filter(usuario=usuario).order_by('-fecha_compra')
    except Usuario.DoesNotExist:
        compras = Compra.objects.none()
        messages.error(request, "Usuario no encontrado")
    
    context = {
        'compras': compras,
    }
    return render(request, 'mis_compras.html', context)

@login_required
def detalle_compra(request, compra_id):
    """Muestra el detalle de una compra específica"""
    try:
        usuario = Usuario.objects.get(nombre_usuario=request.user.username)
        compra = get_object_or_404(Compra, id=compra_id, usuario=usuario)
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado")
        return redirect('core:mis_compras')
    
    context = {
        'compra': compra,
    }
    return render(request, 'detalle_compra.html', context)

# ============================
# VISTAS DE AUTENTICACIÓN
# ============================

def registrar_usuario(request):
    """Registra un nuevo usuario mediante AJAX"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            nombre = request.POST.get('nombre', '')
            
            # Validaciones básicas
            if not all([username, email, password1, password2]):
                return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios'})
            
            if password1 != password2:
                return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden'})
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'El nombre de usuario ya existe'})
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'El email ya está registrado'})
            
            # Crear usuario de Django
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Crear usuario personalizado
            usuario = Usuario.objects.create(
                nombre_usuario=username,
                email=email,
                password_hash=user.password,
                rol='cliente'
            )
            
            # Crear cliente
            cliente = Cliente.objects.create(
                usuario=usuario,
                nombre=nombre or username
            )
            
            # Autenticar al usuario automáticamente
            user_auth = authenticate(username=username, password=password1)
            if user_auth is not None:
                login(request, user_auth)
                return JsonResponse({
                    'success': True, 
                    'message': '¡Registro exitoso! Bienvenido a FlashSnacks',
                    'username': username
                })
            else:
                return JsonResponse({'success': True, 'message': '¡Registro exitoso! Por favor inicia sesión'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error en el registro: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def iniciar_sesion(request):
    """Inicia sesión mediante AJAX"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if not username or not password:
                return JsonResponse({'success': False, 'error': 'Usuario y contraseña son obligatorios'})
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True, 
                    'message': '¡Inicio de sesión exitoso!',
                    'username': user.username
                })
            else:
                return JsonResponse({'success': False, 'error': 'Usuario o contraseña incorrectos'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al iniciar sesión: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def cerrar_sesion(request):
    """Cierra la sesión del usuario"""
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True, 'message': 'Sesión cerrada correctamente'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# ============================
# VISTAS EXISTENTES
# ============================

def home(request):
    return HttpResponse("¡Hola, FlashNacks está en línea!")

def cliente_view(request):
    return render(request, "core/cliente.html")

def menu_negocio_view(request, negocio):
    # CORREGIDO: Ya no usamos inventario__proveedor
    productos = Producto.objects.filter(restaurante__nombre__iexact=negocio, activo=True)
    return render(request, "core/cliente.html", {
        "negocio": negocio,
        "productos": productos
    })
    # En tu views.py - agregar estas vistas
from django.http import JsonResponse
from django.core import serializers
from .models import RestauranteVirtual, Producto

def api_restaurantes(request):
    restaurantes = RestauranteVirtual.objects.all()
    data = {
        'restaurantes': [
            {
                'id': r.id,
                'nombre': r.nombre,
                'descripcion': r.descripcion,
                'costo_envio': float(r.costo_envio),
                'imagen': r.imagen.url if r.imagen else ''
            }
            for r in restaurantes
        ]
    }
    return JsonResponse(data)

def api_menu_restaurante(request, restaurante_id):
    productos = Producto.objects.filter(restaurante_id=restaurante_id)
    data = {
        'productos': [
            {
                'id': p.id,
                'nombre': p.nombre,
                'precio': float(p.precio),
                'descripcion': p.descripcion,
                'imagen': p.imagen.url if p.imagen else ''
            }
            for p in productos
        ]
    }
    return JsonResponse(data)