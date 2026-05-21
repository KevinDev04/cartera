from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --- 1. MODELO DE USUARIO (Solo para el personal: Admin y Cobradores) ---
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
    
    # Datos de entrada del cobrador
    capital_prestado = models.DecimalField(max_digits=12, decimal_places=2)
    porcentaje_interes = models.IntegerField(help_text="Porcentaje de interés mensual (ej. 16)") 
    meses_duracion = models.IntegerField(default=1, help_text="Duración del crédito en meses")
    frecuencia_pago = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES, default='diario')
    fecha_inicio = models.DateField()
    proximo_cobro = models.DateField()
    
    # Campos calculados automáticamente (Dejamos blank=True, null=True para el Admin)
    interes_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_deuda = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    saldo_restante = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    numero_cuotas = models.IntegerField(blank=True, null=True)
    valor_cuota_recomendada = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Crédito #{self.id} - {self.cliente.nombre_completo} (${self.total_deuda})"

    def save(self, *args, **kwargs):
        # PASO 1: Calcular el interés total basado en los meses de duración
        # Fórmula: Capital * (Porcentaje Mensual * Meses) / 100
        porcentaje_total = (Decimal(self.porcentaje_interes) * Decimal(self.meses_duracion)) / Decimal(100)
        self.interes_total = self.capital_prestado * porcentaje_total
        
        # PASO 2: Valor de interés + Capital = Deuda Total
        self.total_deuda = self.capital_prestado + self.interes_total
        
        # PASO 3: Calcular cantidad de cuotas automáticamente según la frecuencia seleccionada
        if self.frecuencia_pago == 'diario':
            self.numero_cuotas = self.meses_duracion * 30
        elif self.frecuencia_pago == 'semanal':
            self.numero_cuotas = self.meses_duracion * 4
        elif self.frecuencia_pago == 'quincenal':
            self.numero_cuotas = self.meses_duracion * 2
        elif self.frecuencia_pago == 'mensual':
            self.numero_cuotas = self.meses_duracion

        # PASO 4: Deuda Total / Cantidad de cuotas = Valor de cuota (Redondeado a pesos Colombianos enteros)
        if self.numero_cuotas > 0:
            cuota_exacta = self.total_deuda / Decimal(self.numero_cuotas)
            self.valor_cuota_recomendada = cuota_exacta.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        
        # Asignar el saldo restante inicial si el préstamo apenas se está creando
        if not self.id:
            self.saldo_restante = self.total_deuda
            
        super().save(*args, **kwargs)


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
    
    # Campo de auditoría empresarial
    editado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Recaudo #{self.id} - {self.prestamo.cliente.nombre_completo} (${self.valor_pagado})"