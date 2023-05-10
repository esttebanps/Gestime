# import time
from django.test import TestCase
# from django.urls import reverse

# from managementime import views
# from managementime import models
# from managementime.forms import TiempoJuegoForm

# Create your tests here.
    # Tests that the form submission with valid data creates a new instance of TiempoJuego and redirects to the success URL. 
    # Tests that the calculation of time and cost with valid input creates a new instance of Precio associated with a new instance of TiempoJuego. 
"""
def test_calculation_valid_input(self):

    #Test that the calculation of time and cost with valid input creates a new instance of Precio associated with a new instance of TiempoJuego.
    
    consola = models.Consola.objects.create(nombre='PS4')
    
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