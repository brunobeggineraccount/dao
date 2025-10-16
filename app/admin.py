from django.contrib import admin
from .models import (
    Especialidad, Medico, Paciente, Turno, 
    HistorialClinico, Receta, Recordatorio
)

# ----------------------------------------------------------------------------------------------------
# INLINES para anidar modelos relacionados
# ----------------------------------------------------------------------------------------------------

# Inline para la relación Muchos a Muchos entre Médico y Especialidad
class EspecialidadInline(admin.TabularInline):
    model = Medico.especialidades.through
    extra = 1
    verbose_name = "Especialidad Asignada"
    verbose_name_plural = "Especialidades del Médico"

# Inline para la relación Uno a Uno de Receta dentro de Historial Clínico
class RecetaInline(admin.StackedInline):
    model = Receta
    can_delete = False  # Para asegurar que la receta se maneje junto al historial
    verbose_name = "Receta Electrónica"
    verbose_name_plural = "Receta Electrónica"
    extra = 0
    max_num = 1 # Solo puede haber una receta por historial

# ----------------------------------------------------------------------------------------------------
# MODELOS BASE (ABM)
# ----------------------------------------------------------------------------------------------------

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion_corta')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if obj.descripcion and len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'apellido', 'nombre', 'email', 'get_especialidades')
    search_fields = ('matricula', 'apellido', 'nombre', 'email')
    ordering = ('apellido', 'nombre')
    
    # Usa el inline para gestionar la relación N:M directamente en el formulario del Médico
    inlines = [EspecialidadInline]
    
    # Excluye el campo ManyToManyField del formulario principal
    # ya que se gestiona mediante el inline.
    exclude = ('especialidades',) 

    def get_especialidades(self, obj):
        return ", ".join([e.nombre for e in obj.especialidades.all()])
    get_especialidades.short_description = 'Especialidades'


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('dni', 'apellido', 'nombre', 'fecha_nacimiento', 'email')
    search_fields = ('dni', 'apellido', 'nombre')
    list_filter = ('fecha_nacimiento',)
    date_hierarchy = 'fecha_nacimiento'
    ordering = ('apellido', 'nombre')

# ----------------------------------------------------------------------------------------------------
# TRANSACCIÓN PRINCIPAL: Turno
# ----------------------------------------------------------------------------------------------------

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'paciente', 'medico', 'estado')
    # Filtros clave para reportes: por estado, médico y fecha
    list_filter = ('estado', 'medico', 'medico__especialidades', 'fecha_hora')
    search_fields = ('paciente__apellido', 'medico__apellido', 'motivo_consulta')
    ordering = ('fecha_hora',)
    date_hierarchy = 'fecha_hora'


# ----------------------------------------------------------------------------------------------------
# GESTIÓN CLÍNICA Y OPCIÓN ADICIONAL
# ----------------------------------------------------------------------------------------------------

@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ('get_paciente_nombre', 'get_medico_nombre', 'fecha_atencion', 'diagnostico_corto')
    # Filtros por médico y fecha
    list_filter = ('turno__medico', 'fecha_atencion')
    search_fields = ('turno__paciente__apellido', 'diagnostico', 'tratamiento')
    ordering = ('-fecha_atencion',)
    
    # Incluimos la Receta como inline
    inlines = [RecetaInline] 

    def get_paciente_nombre(self, obj):
        return str(obj.turno.paciente)
    get_paciente_nombre.short_description = 'Paciente'
    
    def get_medico_nombre(self, obj):
        return str(obj.turno.medico)
    get_medico_nombre.short_description = 'Médico'

    def diagnostico_corto(self, obj):
        return obj.diagnostico[:50] + '...' if len(obj.diagnostico) > 50 else obj.diagnostico
    diagnostico_corto.short_description = 'Diagnóstico'


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('get_paciente', 'fecha_emision', 'medicamentos_cortos')
    search_fields = ('medicamentos', 'historial__turno__paciente__apellido')
    ordering = ('-fecha_emision',)

    def get_paciente(self, obj):
        return str(obj.historial.turno.paciente)
    get_paciente.short_description = 'Paciente'

    def medicamentos_cortos(self, obj):
        return obj.medicamentos[:50] + '...' if len(obj.medicamentos) > 50 else obj.medicamentos
    medicamentos_cortos.short_description = 'Medicamentos Recetados'


@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ('turno', 'tipo', 'fecha_hora_envio', 'enviado')
    list_filter = ('tipo', 'enviado', 'fecha_hora_envio')
    search_fields = ('turno__paciente__apellido', 'turno__medico__apellido')
    ordering = ('-fecha_hora_envio',)
