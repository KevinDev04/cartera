import django.contrib
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cartera.views import ClienteViewSet, FiadorViewSet, PrestamoViewSet, PagoViewSet
from rest_framework.authtoken.views import obtain_auth_token

# El Router genera automáticamente rutas como: /api/clientes/, /api/prestamos/, etc.
router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'fiadores', FiadorViewSet, basename='fiador')
router.register(r'prestamos', PrestamoViewSet, basename='prestamo')
router.register(r'pagos', PagoViewSet, basename='pago')

urlpatterns = [
    path('admin/', django.contrib.admin.site.sender if hasattr(django.contrib.admin.site, 'sender') else django.contrib.admin.site.urls), # Panel normal de Django
    path('api/', include(router.urls)), # 👈 Aquí se conectan todas tus APIs
    path('api/login/', obtain_auth_token, name='api_login'), # 👈 NUEVO ENDPOINT DE LOGIN
    path('', include('cartera.urls')),
    ]