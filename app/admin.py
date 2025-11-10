from django.contrib import admin
from .models import (
    Especialidad, Medico, Paciente, Receta,
    DisponibilidadMedico, Turno, HistorialClinico
)


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    """Configuración para el modelo Especialidad."""
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """Configuración para el modelo Paciente."""
    list_display = ('id', 'dni', 'nombre', 'apellido', 'mail')
    search_fields = ('dni', 'nombre', 'apellido')
    ordering = ('apellido', 'nombre')

class DisponibilidadMedicoInline(admin.TabularInline):
    """Muestra la disponibilidad dentro de la vista de Medico."""
    model = DisponibilidadMedico
    extra = 1 # Número de formularios vacíos para añadir
    fields = ('dia_semana', 'hora_inicio', 'hora_fin')

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'especialidad', 'mail')
    search_fields = ('nombre', 'apellido', 'mail')
    list_filter = ('especialidad',)
    ordering = ('apellido', 'nombre')
    inlines = [DisponibilidadMedicoInline] # Añadimos el inline aquí

@admin.register(DisponibilidadMedico)
class DisponibilidadMedicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'medico', 'dia_semana', 'hora_inicio', 'hora_fin')
    list_filter = ('medico', 'dia_semana')

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    """Configuración para el modelo Turno."""
    list_display = ('id', 'paciente', 'medico', 'fecha', 'estado', 'duracion', 'recordatorio')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'medico__apellido', 'motivo_consulta')
    list_filter = ('estado', 'medico', 'fecha')
    ordering = ('-fecha',) # Ordena por fecha más reciente primero
    date_hierarchy = 'fecha' # Permite navegar por fechas

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    """Configuración para el modelo Receta."""
    list_display = ('id', 'paciente', 'medico', 'descripcion_corta')
    search_fields = ('paciente__nombre', 'medico__nombre', 'descripcion')
    list_filter = ('medico',)

    def descripcion_corta(self, obj):
        """Muestra una vista previa de la descripción."""
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'

# ---

# 7. Historial Clínico
@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    """Configuración para el modelo HistorialClinico."""
    # Como el ID es la clave foránea a Turno, lo mostramos.
    list_display = ('turno', 'paciente', 'descripcion_corta')
    search_fields = ('paciente__nombre', 'descripcion')
    list_filter = ('paciente',)

    def descripcion_corta(self, obj):
        """Muestra una vista previa de la descripción."""
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción del Historial'
