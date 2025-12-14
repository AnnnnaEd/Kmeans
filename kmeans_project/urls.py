from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Incluimos TODAS las URLs de la aplicación en la raíz del proyecto.
    path('', include('fraud_detection_api.urls')),
]