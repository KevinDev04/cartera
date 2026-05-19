from django.db import models
from django.conf import settings # Para referenciar al Custom User correctamente
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --- 1. MODELO DE USUARIO (Solo para el personal) ---
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('collector', 'Cobrador'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='collector')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# --- 2. MODELO: CLIENTE ---
class Cliente(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mis_clientes')
    nombre_completo = models.CharField(max_length=200)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    direccion_residencia = models.TextField()
    direccion_trabajo = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_completo

# --- 3. MODELO: FIADOR ---
class Fiador(models.Model):
    nombre_completo = models.CharField(max_length=200)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    observacion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_completo

# --- 4. MODELO: PRESTAMO ---
class Prestamo(models.Model):
    FRECUENCIA_CHOICES = (
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    )
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('atrasado', 'Atrasado'),
        ('terminado', 'Terminado'),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='prestamos')
    fiador = models.ForeignKey(Fiador, on_delete=models.SET_NULL, null=True, blank=True)
    
    capital_prestado = models.DecimalField(max_digits=12, decimal_places=2)
    porcentaje_interes = models.IntegerField() 
    interes_total = models.DecimalField(max_digits=12, decimal_places=2)
    total_deuda = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_restante = models.DecimalField(max_digits=12, decimal_places=2)
    
    numero_cuotas = models.IntegerField()
    valor_cuota_recomendada = models.DecimalField(max_digits=12, decimal_places=2)
    
    frecuencia_pago = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES, default='diario')
    fecha_inicio = models.DateField()
    proximo_cobro = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

# --- 5. MODELO: PAGO ---
class Pago(models.Model):
    TIPO_PAGO_CHOICES = (
        ('cuota', 'Cuota Normal'),
        ('abono', 'Abono'),
        ('total', 'Pago Total'),
        ('mora', 'Mora'),
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='pagos')
    valor_pagado = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, default='cuota')
    editado = models.BooleanField(default=False)