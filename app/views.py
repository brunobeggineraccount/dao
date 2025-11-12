from rest_framework import viewsets, status
from .models import (
    Especialidad, Medico, Paciente, Receta,
    DisponibilidadMedico, Turno, HistorialClinico
)
from .serializers import (
    EspecialidadSerializer, MedicoSerializer, PacienteSerializer, RecetaSerializer,
    DisponibilidadMedicoSerializer, TurnoSerializer, HistorialClinicoSerializer
)
from django.db import connection
from rest_framework.response import Response

# ViewSet para Especialidad (CRUD completo)
class EspecialidadViewSet(viewsets.ViewSet):
    
    # ----------------------------------------------------
    # 1. LISTAR (GET /app/especialidades/)
    # Comportamiento: Retorna lista de objetos con código 200 OK.
    # ----------------------------------------------------
    def list(self, request):
        sql_query = "SELECT id, nombre FROM app_especialidad ORDER BY nombre ASC"
        
        # Usamos .raw() para obtener objetos Model a partir del SQL.
        queryset = Especialidad.objects.raw(sql_query)
        
        serializer = EspecialidadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ----------------------------------------------------
    # 2. CREAR (POST /app/especialidades/)
    # Comportamiento: Retorna el objeto creado con código 201 Created.
    # ----------------------------------------------------
    def create(self, request):
        data = request.data
        
        # 1. Validar la data (como lo haría un ModelViewSet)
        serializer = EspecialidadSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            with connection.cursor() as cursor:
                # Query de INSERT con SQL puro. RETURNING id es clave.
                cursor.execute(
                    """
                    INSERT INTO app_especialidad (nombre)
                    VALUES (%s)
                    RETURNING id
                    """,
                    [data['nombre']]
                )
                new_id = cursor.fetchone()[0]
            
            # Devolvemos la respuesta formateada con el nuevo ID y código 201
            created_data = {'id': new_id, 'nombre': data['nombre']}
            return Response(created_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Manejo de errores de la DB
            return Response({'detail': f'Error SQL al crear: {e}'}, 
                            status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------
    # 3. DETALLE (GET /app/especialidades/{id}/)
    # Comportamiento: Retorna el objeto con código 200 OK o 404 Not Found.
    # ----------------------------------------------------
    def retrieve(self, request, pk=None):
        try:
            # Usamos el ORM para obtener la instancia (más seguro que raw)
            instance = get_object_or_404(Especialidad, pk=pk)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        # Ejecutamos nuestra query SQL para obtener los datos
        sql_query = "SELECT id, nombre FROM app_especialidad WHERE id = %s"
        
        # Usamos .raw() solo para simular que la lectura viene de SQL
        queryset = Especialidad.objects.raw(sql_query, [pk])
        
        # Obtenemos el primer (y único) resultado
        try:
            data_instance = queryset.model.objects.get(pk=pk)
        except Especialidad.DoesNotExist:
             return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = EspecialidadSerializer(data_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # ----------------------------------------------------
    # 4. ACTUALIZAR (PUT /app/especialidades/{id}/)
    # Comportamiento: Retorna el objeto actualizado con código 200 OK.
    # ----------------------------------------------------
    def update(self, request, pk=None):
        data = request.data
        
        # 1. Validación de datos
        serializer = EspecialidadSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with connection.cursor() as cursor:
                # Query de UPDATE con SQL puro
                cursor.execute(
                    """
                    UPDATE app_especialidad SET nombre = %s
                    WHERE id = %s
                    """,
                    [data['nombre'], pk]
                )
            
            # Devolvemos el objeto actualizado
            updated_data = {'id': int(pk), 'nombre': data['nombre']}
            return Response(updated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'detail': f'Error SQL al actualizar: {e}'}, 
                            status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------
    # 5. ELIMINAR (DELETE /app/especialidades/{id}/)
    # Comportamiento: Retorna un código 204 No Content.
    # ----------------------------------------------------
    def destroy(self, request, pk=None):
        try:
            with connection.cursor() as cursor:
                # Query de DELETE con SQL puro
                cursor.execute(
                    "DELETE FROM app_especialidad WHERE id = %s",
                    [pk]
                )
            
            # Devolvemos una respuesta 204 sin contenido
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            # Capturar errores de integridad referencial
            return Response({'detail': f'Error SQL al eliminar: {e}'}, 
                            status=status.HTTP_400_BAD_REQUEST)

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
