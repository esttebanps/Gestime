from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index),
    path('registrar/',TiempoJuegoCreateView.as_view(), name='crear_tiempo_juego'),
    #path('tiempos-juego/', VerTiemposDeJuegoView.as_view(), name='tiempos-juego'),
]