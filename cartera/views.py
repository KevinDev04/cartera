from django.shortcuts import render

from rest_framework import viewsets, permissions
from .models import Cliente, Fiador, Prestamo, Pago
from .serializers import ClienteSerializer, FiadorSerializer, PrestamoSerializer, PagoSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    # Obliga a que el usuario esté autenticado para usar la API
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # FILTRO SENIOR: El cobrador SOLO ve los clientes que él registró
        user = self.request.user
        if user.role == 'admin':
            return Cliente.objects.filter(activo=True) # El administrador ve todo
        return Cliente.objects.filter(usuario=user, activo=True)

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
