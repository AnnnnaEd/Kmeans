from django.urls import path
from .views import RunKMeansView, frontend_view

urlpatterns = [
    # API endpoint (la ruta completa es ahora /api/analyze/)
    path('api/analyze/', RunKMeansView.as_view(), name='run-kmeans-analysis'),
    
    # Frontend/Index view (la ruta completa es ahora /)
    path('', frontend_view, name='frontend'),
]