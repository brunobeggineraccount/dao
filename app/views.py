from rest_framework import viewsets
from .models import (
    Especialidad, Medico, Paciente, Receta,
    DisponibilidadMedico, Turno, HistorialClinico
)
from .serializers import (
    EspecialidadSerializer, MedicoSerializer, PacienteSerializer, RecetaSerializer,
    DisponibilidadMedicoSerializer, TurnoSerializer, HistorialClinicoSerializer
)

# ViewSet para Especialidad (CRUD completo)
class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer

# ---

# ViewSet para Paciente (CRUD completo)
class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

# ---

# ViewSet para Médico (CRUD completo)
class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer

# ---

# ViewSet para Turno (CRUD completo)
class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    filterset_fields = ['medico', 'paciente', 'estado'] # Opcional: para filtrar por campos

# ---

# ViewSet para Receta (CRUD completo)
class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer

# ---

# ViewSet para DisponibilidadMedico (CRUD completo)
class DisponibilidadMedicoViewSet(viewsets.ModelViewSet):
    queryset = DisponibilidadMedico.objects.all()
    serializer_class = DisponibilidadMedicoSerializer

# ---

# ViewSet para HistorialClinico (CRUD completo)
class HistorialClinicoViewSet(viewsets.ModelViewSet):
    queryset = HistorialClinico.objects.all()
    serializer_class = HistorialClinicoSerializer
