import datetime
from datetime import date
from django.shortcuts import render
from django.views.generic.edit import CreateView
from .forms import TiempoJuegoForm
from .models import Consola, TiempoJuego, Precio

def index(request):
    return render(request, 'base.html')

class TiempoJuegoCreateView(CreateView):
    template_name = 'tiempojuego_form.html'
    model = TiempoJuego
    form_class = TiempoJuegoForm
    success_url = '/'

    def form_valid(self, form):
        """
        Obtener la instancia de TiempoJuego a partir del formulario.
        """
        tiempo_juego = form.save(commit=False)
        
        """
        Este código obtiene la hora actual y la asigna al campo "hora_inicio" de una instancia de TiempoJuego.
        """
        now = datetime.datetime.now()
        hora_inicio = datetime.time(hour=now.hour, minute=now.minute, second=now.second)
        tiempo_juego.hora_inicio = hora_inicio
        
        """
        Este fragmento verifica si se proporcionaron las horas y los minutos para calcular la hora de finalización 
        y si es así, lo calcula.
        Si no se proporcionaron las horas y los minutos pero se proporcionó la hora de finalización,
        calcula la duración y actualiza las horas y minutos. 
        Si no se proporcionó ni la hora de finalización ni las horas y minutos, 
        establece la hora de finalización en 00:00:00 y las horas y minutos en 0.
        """
        if tiempo_juego.horas is not None and tiempo_juego.minutos is not None:
            delta = datetime.timedelta(hours=tiempo_juego.horas, minutes=tiempo_juego.minutos)
            hora_fin = (datetime.datetime.combine(datetime.date.today(), hora_inicio) + delta).time()
            tiempo_juego.hora_fin = hora_fin
        elif tiempo_juego.hora_fin is not None: 
            hora_fin = tiempo_juego.hora_fin
            datetime1 = datetime.datetime.combine(date.today(), hora_inicio)    
            datetime2 = datetime.datetime.combine(date.today(), hora_fin)
            hora_fin = datetime2 - datetime1
            tiempo_juego.horas = hora_fin.seconds // 3600
            tiempo_juego.minutos = (hora_fin.seconds // 60) % 60
            #print(f"Horas: {tiempo_juego.horas}, minutos: {tiempo_juego.minutos}")
        else:
            tiempo_juego.horas = 0
            tiempo_juego.minutos = 0 
            tiempo_juego.hora_fin = datetime.time(hour=0, minute=0, second=0)
        #print(f"es resultado es: {tiempo_juego.hora_fin}")
        #print(f"es resultado es: {datetime1}, {datetime2}")
        #print(f"es resultado es: {tiempo_juego.horas}, {tiempo_juego.minutos}")
        
        tiempo_juego.save()
        #print(f"resultado despues de guardar: {tiempo_juego.horas}, {tiempo_juego.minutos}")
        
        """
        Este fragmento calcula el costo del tiempo de juego y el costo adicional por control extra 
        en función de los datos del formulario y crea un objeto Precio asociado a un objeto TiempoJuego.
        """
        control_extra = form.cleaned_data['control_extra']
        
        if control_extra is not None:
            costo_control = control_extra * 500
        horasc = tiempo_juego.horas
        minutosc = tiempo_juego.minutos
        #print(f"horas para cleaned_data: {horasc}, {minutosc}")
        costo_tiempo = (horasc * 60 + minutosc) * 50
        costo_total = costo_control + costo_tiempo
        
        precio = Precio()
        precio.costo_control = costo_control
        precio.costo_tiempo = costo_tiempo
        precio.costo_total = costo_total
        
        precio.tiempo_juego = tiempo_juego
        precio.save()
        
        return super().form_valid(form)
            
        
        
        
        
        
"""
        if tiempo_juego.horas is not None and tiempo_juego.minutos is not None:
            # Calcular la hora de finalización.
            tiempo_fin = datetime.datetime.combine(datetime.datetime.now().date(), horas) + datetime.timedelta(hours=tiempo_juego.horas, minutes=tiempo_juego.minutos)
            tiempo_juego.hora_fin = tiempo_fin.time()
            
        elif tiempo_juego.hora_fin is None:
            tiempo_juego.hora_fin = None
            
        tiempo_juego.save()
        
        # Calcular los campos del modelo Precio.
        horas = form.cleaned_data['horas']
        minutos = form.cleaned_data['minutos']
        control_extra = form.cleaned_data['control_extra']
        costo_control = 500  # Puedes usar una constante o un valor calculado dinámicamente.
        costo_tiempo = (horas * 60 + minutos) * 50
        total_control_extra = control_extra * costo_control
        costo_total = costo_control + costo_tiempo + total_control_extra
            

        # Crear una instancia de Precio y asignar los valores.
        precio = Precio()
        precio.costo_control = total_control_extra
        precio.costo_tiempo = costo_tiempo
        precio.costo_total = costo_total
        
        # Asignar la instancia de TiempoJuego y guardar ambas instancias.
        precio.tiempo_juego = tiempo_juego
        precio.save()

        return super().form_valid(form)
"""  


