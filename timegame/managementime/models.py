from datetime import *
from django.db import models



class Consola(models.Model):
    nombre = models.CharField(max_length=100)

class TiempoJuego(models.Model):
    consola = models.ForeignKey(Consola, on_delete=models.CASCADE)
    horas = models.IntegerField(blank=True, null=True)
    minutos = models.IntegerField(blank=True, null=True)
    hora_inicio = models.TimeField(null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    control_extra = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

class Precio(models.Model):
    tiempo_juego = models.OneToOneField(TiempoJuego, on_delete=models.CASCADE)
    costo_control = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    costo_tiempo = models.DecimalField(max_digits=6, decimal_places=1)
    costo_total = models.DecimalField(max_digits=6, decimal_places=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)











































"""class Consola(models.Model):
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre

class TiempoJuego(models.Model):
    horas = models.IntegerField(default=0)
    minutos = models.IntegerField(default=0)
    hora_inicio = models.DateTimeField(auto_now=False, auto_now_add=False)
    hora_fin = models.DateTimeField(auto_now=False, auto_now_add=False)
    control_extra = models.IntegerField(default=0)
    costo_control = models.IntegerField(default=0)
    costo_tiempo = models.IntegerField(default=0)
    costo_total = models.IntegerField(default=0)
    is_completed = models.BooleanField()
    fecha_creacion = models.DateField(auto_now=False, auto_now_add=True)
    consola = models.ForeignKey("managementime.Consola", on_delete=models.CASCADE)

    def __str__(self):
        return self.consola.nombre
"""