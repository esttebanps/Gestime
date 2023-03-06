from django import forms
from django.forms.widgets import *
from .models import *

class TiempoJuegoForm(forms.ModelForm):
    hora_fin = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'step': 60, 'format': '%H:%M'}))
    class Meta:
        model = TiempoJuego
        fields = ['consola', 'horas', 'minutos','hora_fin','control_extra', 'is_completed']
        required = {
            'horas': True,
            'minutos': True,
            'hora_fin': True,
        }
        
        

# para despues: attrs={'class': 'form-control'}