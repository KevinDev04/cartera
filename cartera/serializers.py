from rest_framework import serializers
from .models import User, Cliente, Fiador, Prestamo, Pago

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone']

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        # El campo usuario se puede rellenar automáticamente en la vista
        read_only_fields = ['usuario'] 

class FiadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fiador
        fields = '__all__'

class PrestamoSerializer(serializers.ModelSerializer):
    # Mostramos detalles del cliente en las consultas, pero permitimos escribir el ID
    cliente_detalle = ClienteSerializer(source='cliente', read_only=True)

    class Meta:
        model = Prestamo
        fields = '__all__'
        # Estos campos los calcula el método save() del modelo, la API no debe exigirlos
        read_only_fields = [
            'usuario', 'interes_total', 'total_deuda', 
            'saldo_restante', 'numero_cuotas', 'valor_cuota_recomendada'
        ]

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'
        read_only_fields = ['usuario', 'fecha_pago', 'editado']