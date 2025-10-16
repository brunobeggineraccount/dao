from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

# ----------------------------------------------------------------------------------------------------
# ENTIDADES BASE: ABM de pacientes, médicos y especialidades
# ----------------------------------------------------------------------------------------------------
DURATION = 30

class Especialidad(models.Model):
    """Representa una especialidad médica (ej: Cardiología, Pediatría)."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Especialidad")
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Especialidades"
        ordering = ['nombre']

    def __str__(self):
        return str(self.nombre)

class Medico(models.Model):
    """Representa al personal médico."""
    matricula = models.CharField(max_length=50, unique=True, verbose_name="Matrícula Profesional")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    # Relación N:M (Muchos a Muchos) con Especialidad
    especialidades = models.ManyToManyField(Especialidad, related_name='medicos')

    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"Dr. {self.apellido}, {self.nombre} ({self.matricula})"

class Paciente(models.Model):
    """Representa a un paciente del sistema."""
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    email = models.EmailField(blank=True, null=True) # Necesario para Recordatorios (Opcional)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"

# ----------------------------------------------------------------------------------------------------
# TRANSACCIÓN PRINCIPAL: Turnos
# ----------------------------------------------------------------------------------------------------

class Turno(models.Model):
    """Representa un turno médico agendado."""

    # Campo clave para Reportes (Asistencia vs. Inasistencia)
    ESTADOS_TURNO = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('ATENDIDO', 'Atendido (Asistencia)'),
        ('CANCELADO', 'Cancelado'),
        ('AUSENTE', 'Ausente (Inasistencia)'),
    ]

    # Relación N:1 (Muchos a Uno)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='turnos')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='turnos')

    fecha_hora = models.DateTimeField(verbose_name="Fecha y Hora del Turno")
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS_TURNO,
        default='PENDIENTE'
    )
    motivo_consulta = models.TextField(blank=True, null=True)
    duration = models.IntegerField(default=DURATION)

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ['fecha_hora']
        # Validación de horarios: Un médico no puede tener dos turnos a la misma hora exacta.
        unique_together = ('medico', 'fecha_hora')

    def clean(self):
        """Validación de superposición (lógica de negocio más allá del unique_together)."""
        assert isinstance(self.fecha_hora, datetime.datetime)
        duracion_turno = datetime.timedelta(minutes=DURATION)
        
        hora_fin = self.fecha_hora + duracion_turno

        superposiciones = Turno.objects.filter(
            medico=self.medico,
            fecha_hora__lt=hora_fin,  # Turnos que empiezan antes de que este termine
            fecha_hora__gt=self.fecha_hora - duracion_turno # Turnos que terminan después de que este empiece
        ).exclude(pk=self.pk) # Excluye el turno actual si es una modificación

        superposiciones = superposiciones.exclude(estado__in=['CANCELADO', 'AUSENTE'])

        if superposiciones.exists():
            raise ValidationError(
                'El médico ya tiene un turno asignado que se superpone con este horario.'
            )

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        assert isinstance(self.fecha_hora, datetime.datetime)
        return f"Turno {self.estado} de {self.paciente} con Dr. {self.medico} el {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"


class HistorialClinico(models.Model):
    """Representa la atención médica generada a partir de un turno."""
    
    # Relación 1:1 (Uno a Uno) con Turno
    # Un registro de historial debe estar asociado a una atención específica.
    turno = models.OneToOneField(
        Turno, 
        on_delete=models.CASCADE, 
        related_name='historial',
        verbose_name="Turno/Atención Asociada"
    )

    fecha_atencion = models.DateField(default=timezone.now, verbose_name="Fecha de Atención")
    diagnostico = models.TextField(verbose_name="Diagnóstico")
    tratamiento = models.TextField(blank=True, null=True, verbose_name="Tratamiento / Indicaciones")

    class Meta:
        verbose_name = "Historial Clínico"
        verbose_name_plural = "Historiales Clínicos"
        ordering = ['-fecha_atencion']

    def __str__(self):
        assert isinstance(self.turno, Turno)
        return f"Historial de {self.turno.paciente} del {self.fecha_atencion}"

class Receta(models.Model):
    """Representa una receta médica electrónica."""
    
    # Relación 1:1 (Uno a Uno) con HistorialClinico
    # Una receta es parte del historial de una atención.
    historial = models.OneToOneField(
        HistorialClinico, 
        on_delete=models.CASCADE, 
        related_name='receta',
        verbose_name="Atención del Historial"
    )
    fecha_emision = models.DateField(default=timezone.now, verbose_name="Fecha de Emisión")
    medicamentos = models.TextField(verbose_name="Detalle de Medicamentos")
    indicaciones = models.TextField(blank=True, null=True, verbose_name="Instrucciones Adicionales")

    class Meta:
        verbose_name = "Receta Electrónica"
        verbose_name_plural = "Recetas Electrónicas"
        ordering = ['-fecha_emision']

    def __str__(self):
        assert isinstance(self.historial, HistorialClinico)
        assert isinstance(self.historial.turno, Turno)
        return f"Receta para {self.historial.turno.paciente} ({self.fecha_emision})"

# ----------------------------------------------------------------------------------------------------
# OPCIÓN ADICIONAL: Recordatorios (Mayor Complejidad)
# ----------------------------------------------------------------------------------------------------

class Recordatorio(models.Model):
    """Módulo para el envío de recordatorios automáticos de turnos."""

    TIPOS_ENVIO = [
        ('MAIL', 'Correo Electrónico'),
        ('SMS', 'Mensaje de Texto (SMS)'),
        ('NOTIF', 'Notificación en App'),
    ]

    # Relación N:1 (Muchos a Uno) con Turno
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name='recordatorios')
    tipo = models.CharField(max_length=10, choices=TIPOS_ENVIO, default='MAIL')
    fecha_hora_envio = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora de Envío")
    enviado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Recordatorio"
        verbose_name_plural = "Recordatorios"
        ordering = ['fecha_hora_envio']
        
    def __str__(self):
        return f"Recordatorio ({self.tipo}) para el turno de {self.turno.paciente}."
