from rest_framework import serializers
from .models import (
    Especialidad, Medico, Paciente, Receta,
    DisponibilidadMedico, Turno, HistorialClinico
)

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__' # Incluye todos los campos

class MedicoSerializer(serializers.ModelSerializer):
    especialidad_nombre = serializers.StringRelatedField(source='especialidad')

    class Meta:
        model = Medico
        fields = '__all__'

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

class DisponibilidadMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisponibilidadMedico
        exclude = ('medico',)

class TurnoSerializer(serializers.ModelSerializer):
    # Para mostrar el nombre completo del paciente y médico
    paciente_nombre_completo = serializers.StringRelatedField(source='paciente')
    medico_nombre_completo = serializers.StringRelatedField(source='medico')

    class Meta:
        model = Turno
        fields = '__all__'

class RecetaSerializer(serializers.ModelSerializer):
    medico_nombre = serializers.StringRelatedField(source='medico')
    paciente_nombre = serializers.StringRelatedField(source='paciente')
    
    class Meta:
        model = Receta
        fields = '__all__'

class HistorialClinicoSerializer(serializers.ModelSerializer):
    turno_id = serializers.PrimaryKeyRelatedField(source='turno', read_only=True)
    class Meta:
        model = HistorialClinico
        fields = ('turno_id', 'paciente', 'descripcion')
