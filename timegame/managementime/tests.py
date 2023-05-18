# import time
from django.test import TestCase
# from django.urls import reverse

# from managementime import views
# from managementime import models
# from managementime.forms import TiempoJuegoForm

"""
def test_calculation_valid_input(self):
    
    consola = models.Consola.objects.create(nombre='Consola 1')
    
    tiempo_juego = models.TiempoJuego.objects.create(
        consola=consola,
        horas=2,
        minutos=30,
        hora_inicio=time(hour=10, minute=0, second=0),
        is_active=True
    )
    
    form_data = {
        'control_extra': 2
    }
    form = TiempoJuegoForm(data=form_data)
    self.assertTrue(form.is_valid())

    response = self.client.post(reverse('tiempo_juego_create'), data=form_data)
    self.assertEqual(response.status_code, 302)
    
    self.assertEqual(models.Precio.objects.count(), 1)
"""