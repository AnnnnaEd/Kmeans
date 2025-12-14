# fraud_detection_api/views.py

import tempfile
import os
# Mueve todas las importaciones de Django/DRF/Terceros aquí arriba
from django.shortcuts import render 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import FraudDetectionSerializer
from .analysis import run_kmeans_analysis

class RunKMeansView(APIView):
    """
    Endpoint para subir un CSV y ejecutar el análisis K-Means.
    """
    def post(self, request, *args, **kwargs):
        # 1. Validar la entrada (el archivo CSV)
        serializer = FraudDetectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        csv_file = serializer.validated_data['csv_file']
        n_clusters = serializer.validated_data['n_clusters']

        # 2. Guardar el archivo temporalmente
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, csv_file.name)

        try:
            # Escribir el contenido del archivo subido en el archivo temporal
            with open(temp_path, 'wb+') as destination:
                for chunk in csv_file.chunks():
                    destination.write(chunk)

            # 3. Ejecutar el análisis
            analysis_results = run_kmeans_analysis(temp_path, n_clusters)
            
            # 4. Devolver la respuesta
            if "error" in analysis_results:
                return Response(analysis_results, status=status.HTTP_400_BAD_REQUEST)
                
            return Response(analysis_results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error interno del servidor: {e}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # 5. Limpiar el archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)


def frontend_view(request):
    """
    Renderiza la interfaz de usuario (el template principal).
    """
    return render(request, 'fraud_detection_api/index.html')