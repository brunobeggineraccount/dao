from django.db import models

class Especialidad(models.Model):
    """Representa las diferentes especialidades médicas."""
    nombre = models.CharField(max_length=255) # varchar

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Especialidades"

# ---

class Medico(models.Model):
    """Representa a los médicos del sistema."""
    nombre = models.CharField(max_length=255) 
    apellido = models.CharField(max_length=255)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT) 
    mail = models.CharField(max_length=255) 

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name_plural = "Médicos"

# ---

class Paciente(models.Model):
    """Representa a los pacientes del sistema."""
    dni = models.CharField(max_length=255, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True) 
    apellido = models.CharField(max_length=255, blank=True, null=True)
    mail = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"

    class Meta:
        verbose_name_plural = "Pacientes"

# ---

class Receta(models.Model):
    """Representa las recetas médicas emitidas."""
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='recetas_emitidas')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='recetas_recibidas') 
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Receta {self.pk} para {self.paciente}"

    class Meta:
        verbose_name_plural = "Recetas"

# ---

class DisponibilidadMedico(models.Model):
    """Representa los horarios de disponibilidad de cada médico."""
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE) 
    dia_semana = models.IntegerField(null=True, blank=True) 
    hora_inicio = models.TimeField(null=True, blank=True) 
    hora_fin = models.TimeField(null=True, blank=True) 

    def __str__(self):
        return f"Disp. {self.medico} - Día {self.dia_semana}"

    class Meta:
        verbose_name_plural = "Disponibilidad de Médicos"

# ---

class Turno(models.Model):
    """Representa las citas o turnos programados."""
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Confirmado', 'Confirmado'),
        ('Cancelado', 'Cancelado'),
        ('Completado', 'Completado'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='turnos_paciente') 
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='turnos_medico') 
    fecha = models.DateTimeField() 
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Pendiente') 
    motivo_consulta = models.TextField(blank=True, null=True)
    duracion = models.IntegerField() 
    recordatorio = models.CharField(max_length=10)

    def __str__(self):
        return f"Turno {self.pk} de {self.paciente} con {self.medico} el {self.fecha.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name_plural = "Turnos"

# ---

class HistorialClinico(models.Model):
    """Representa el historial clínico asociado a un turno específico."""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE) 
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE, primary_key=True)
    descripcion = models.TextField(null=True, blank=True) # text

    def __str__(self):
        return f"Historial para {self.paciente} (Turno: {self.turno.pk})"

    class Meta:
        verbose_name_plural = "Historiales Clínicos"
