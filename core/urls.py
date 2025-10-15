from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Páginas principales
    path("", views.index, name="index"),
    path("restaurante/<int:restaurante_id>/", views.menu_restaurante, name="menu_restaurante"),
    path("producto/<int:producto_id>/", views.detalle_producto, name="detalle_producto"),
    
    # Carrito
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<int:producto_id>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/actualizar/<int:item_id>/", views.actualizar_carrito, name="actualizar_carrito"),
    path("carrito/eliminar/<int:item_id>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),
    path("carrito/limpiar/", views.limpiar_carrito, name="limpiar_carrito"),
    
    # Compras
    path("comprar/", views.comprar_ahora, name="comprar_ahora"),
    path("mis-compras/", views.mis_compras, name="mis_compras"),
    path("mis-compras/<int:compra_id>/", views.detalle_compra, name="detalle_compra"),
    
    # Autenticación
    path("registrar/", views.registrar_usuario, name="registrar_usuario"),
    path("iniciar-sesion/", views.iniciar_sesion, name="iniciar_sesion"),
    path("cerrar-sesion/", views.cerrar_sesion, name="cerrar_sesion"),
    
    # URLs existentes
    path("home/", views.home, name="home"),
    path("cliente/", views.cliente_view, name="cliente"),
    path("cliente/<str:negocio>/", views.menu_negocio_view, name="menu_negocio"),
    
    # ✅ NUEVAS APIs JSON
    path('api/restaurantes/', views.api_restaurantes, name='api_restaurantes'),
    path('api/restaurante/<int:restaurante_id>/', views.api_menu_restaurante, name='api_menu_restaurante'),
]