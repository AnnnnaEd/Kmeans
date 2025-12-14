# fraud_detection_api/serializers.py
from rest_framework import serializers

class FraudDetectionSerializer(serializers.Serializer):
    """
    Serializador para aceptar un archivo CSV subido por el usuario.
    """
    csv_file = serializers.FileField()
    # n_clusters es opcional, si quieres que el usuario lo especifique
    n_clusters = serializers.IntegerField(required=False, default=5)