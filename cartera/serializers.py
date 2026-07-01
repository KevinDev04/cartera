from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import User, Cliente, Fiador, Prestamo, Pago
from datetime import date

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
    fiador_detalle = FiadorSerializer(source='fiador', read_only=True)
    
    # Si quieres ver detalles básicos del usuario que creó el préstamo (ID y username)
    # Puedes usar un StringRelatedField o crear un serializador básico si lo prefieres.
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

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


class ClienteFormularioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        # Campos que el frontend va a enviar para el cliente
        fields = ['nombre_completo', 'cedula', 'telefono', 'direccion_residencia']        
class CrearCreditoSerializer(serializers.Serializer):
    # --- BLOQUE A: DEFINICIÓN DE LOS CAMPOS RECIBIDOS ---
    # Aquí el mesero anota qué datos está obligado a traer Angular desde el formulario.
    cedula = serializers.CharField(max_length=20)
    
    # Ponemos "required=False" porque si el cliente ya existe, 
    # el cobrador no necesita volver a escribir estos tres campos.
    nombre_completo = serializers.CharField(max_length=200, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    direccion_residencia = serializers.CharField(required=False, allow_blank=True)
    
    # Datos financieros obligatorios para poder computar el crédito
    capital_prestado = serializers.DecimalField(max_digits=12, decimal_places=2)
    porcentaje_interes = serializers.IntegerField()
    meses_duracion = serializers.IntegerField()
    frecuencia_pago = serializers.CharField(max_length=20)

    # --- BLOQUE B: LA LOGICA DE CREACIÓN ---
    # Este método se activa automáticamente cuando la vista le dice "serializer.save()"
    def create(self, validated_data):
        # 1. Identificar al cobrador:
        usuario_actual = self.context['request'].user
        if usuario_actual.is_anonymous:
            User = get_user_model()
            usuario_actual = User.objects.first()

        # Extraemos la cédula para hacer la validación inteligente
        cedula_cliente = validated_data['cedula']

        # 2. El escudo protector (transaction.atomic):
        # Esto es vital en sistemas financieros. Le dice a la base de datos: 
        # "O guardas el cliente y el préstamo JUNTOS, o si uno falla, borras todo". 
        # Evita que te queden créditos huérfanos o clientes a medias.
        with transaction.atomic():
            
            # 3. Buscar o Crear el Cliente de forma inteligente:
            # get_or_create busca en la tabla Cliente si ya hay alguien con esa 'cedula'.
            # - Si lo encuentra: lo guarda en la variable 'cliente' y pone 'created=False'.
            # - Si NO lo encuentra: toma los datos de 'defaults' y lo crea de cero en la tabla.
            cliente, created = Cliente.objects.get_or_create(
                cedula=cedula_cliente,
                defaults={
                    'usuario': usuario_actual,
                    'nombre_completo': validated_data.get('nombre_completo', 'Cliente Registrado'),
                    'telefono': validated_data.get('telefono', ''),
                    'direccion_residencia': validated_data.get('direccion_residencia', '')
                }
            )

            # 4. Crear el Préstamo en su tabla correspondiente:
            # Vinculamos al 'cliente' (ya sea el viejo que encontramos o el nuevo que se creó).
            # Al usar Prestamo.objects.create(), Django viaja a tu 'models.py' y activa 
            # de inmediato el método 'save()' para hacer las matemáticas de las cuotas.
            prestamo = Prestamo.objects.create(
                usuario=usuario_actual,
                cliente=cliente,
                capital_prestado=validated_data['capital_prestado'],
                porcentaje_interes=validated_data['porcentaje_interes'],
                meses_duracion=validated_data['meses_duracion'],
                frecuencia_pago=validated_data['frecuencia_pago'],
                fecha_inicio=date.today(),
                proximo_cobro=date.today()
            )
            
        # Devolvemos el préstamo cocinado listo para que la vista lo use
        return prestamo