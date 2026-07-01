from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny
from .models import Cliente, Fiador, Prestamo, Pago
from .serializers import ClienteSerializer, FiadorSerializer, PrestamoSerializer, PagoSerializer, CrearCreditoSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    # Obliga a que el usuario esté autenticado para usar la API
    permission_classes = [permissions.IsAuthenticated]

    queryset = Cliente.objects.all() 
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Inyecta automáticamente el usuario que está logueado como dueño del cliente
        serializer.save(usuario=self.request.user)


class FiadorViewSet(viewsets.ModelViewSet):
    queryset = Fiador.objects.filter(activo=True)
    serializer_class = FiadorSerializer
    permission_classes = [permissions.IsAuthenticated]


class PrestamoViewSet(viewsets.ModelViewSet):
    serializer_class = PrestamoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # FILTRO SENIOR: Un cobrador solo ve sus préstamos en calle
        user = self.request.user
        if user.role == 'admin':
            return Prestamo.objects.filter(activo=True)
        return Prestamo.objects.filter(usuario=user, activo=True)

    def perform_create(self, serializer):
        # El préstamo se amarra automáticamente al cobrador que lo crea
        serializer.save(usuario=self.request.user)


class PagoViewSet(viewsets.ModelViewSet):
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # FILTRO SENIOR: Un cobrador solo ve su historial de recaudos
        user = self.request.user
        if user.role == 'admin':
            return Pago.objects.filter(activo=True)
        return Pago.objects.filter(usuario=user, activo=True)

    def perform_create(self, serializer):
        pago = serializer.save(usuario=self.request.user)
        
        # LÓGICA DE NEGOCIO: Descontar el saldo restante del préstamo asociado
        prestamo = pago.prestamo
        prestamo.saldo_restante -= pago.valor_pagado
        
        # Si la deuda se liquida por completo, cerramos el préstamo automáticamente
        if prestamo.saldo_restante <= 0:
            prestamo.saldo_restante = 0
            prestamo.estado = 'terminado'
            
        prestamo.save()


class CrearCreditoAPIView(APIView):
    # Excepción de seguridad temporal para que Angular pueda enviar datos sin token de Login
    permission_classes = [AllowAny] 

    # Definimos el método POST porque es una acción para "enviar/guardar" datos
    def post(self, request):
        
        # 1. Le entregamos los datos que llegaron de Angular (request.data) al mesero (Serializer)
        serializer = CrearCreditoSerializer(data=request.data, context={'request': request})
        
        # 2. Control de calidad: Revisa si el formato cumple las reglas del Paso 1
        if serializer.is_valid():
            
            # Si los datos son válidos, ejecuta el método create() del serializer
            prestamo_creado = serializer.save()
            
            # 3. Respuesta Exitosa (Status 201 Created):
            # Le devolvemos un JSON a Angular confirmándole que escribimos en ambas tablas 
            # y le mostramos los cálculos automáticos que Django procesó en el backend.
            return Response({
                "message": "¡Cliente y Crédito procesados con éxito en la BD! 🚀",
                "cliente_asociado": prestamo_creado.cliente.nombre_completo,
                "prestamo_id": prestamo_creado.id,
                "total_deuda_calculada": prestamo_creado.total_deuda,
                "cuotas_totales": prestamo_creado.numero_cuotas,
                "valor_de_cada_cuota": prestamo_creado.valor_cuota_recomendada
            }, status=status.HTTP_201_CREATED)
        
        # 4. Respuesta de Error (Status 400 Bad Request):
        # Si Angular mandó algo mal (ej. letras en el capital prestado), Django frena 
        # la operación y le devuelve al frontend una lista detallada con los errores.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny]) # Excepción temporal para pruebas
def buscar_cliente_por_cedula(request, cedula):
    """
    Esta vista recibe una cédula por la URL. 
    Si la encuentra en la BD, le devuelve a Angular los datos del cliente.
    Si no existe, devuelve un mensaje diciendo que es un cliente nuevo.
    """
    try:
        cliente = Cliente.objects.get(cedula=cedula)
        # Si lo encuentra, arma un paquete con sus datos guardados
        return Response({
            "existe": True,
            "nombre_completo": cliente.nombre_completo,
            "telefono": cliente.telefono,
            "direccion_residencia": cliente.direccion_residencia
        }, status=status.HTTP_200_OK)
    except Cliente.DoesNotExist:
        # Si no lo encuentra, le avisa a Angular que el camino está libre para registrarlo
        return Response({"existe": False}, status=status.HTTP_200_OK)