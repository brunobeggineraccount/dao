from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EspecialidadViewSet, MedicoViewSet, PacienteViewSet, RecetaViewSet,
    DisponibilidadMedicoViewSet, TurnoViewSet, HistorialClinicoViewSet
)

app_name = "app"

router = DefaultRouter()
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'medicos', MedicoViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'turnos', TurnoViewSet)
router.register(r'recetas', RecetaViewSet)
router.register(r'disponibilidad', DisponibilidadMedicoViewSet)
router.register(r'historiales', HistorialClinicoViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
