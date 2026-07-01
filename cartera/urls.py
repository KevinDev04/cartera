from django.urls import path
from .views import *

urlpatterns = [
    # Cuando alguien entre a /api/creditos/crear/, se dispara tu vista
    path('api/creditos/crear/', CrearCreditoAPIView.as_view(), name='crear_credito'),
    path('api/clientes/buscar/<str:cedula>/', buscar_cliente_por_cedula, name='buscar_cliente'),
]