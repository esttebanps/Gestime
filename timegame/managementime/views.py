import datetime
from datetime import date, timedelta, time
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F, Sum
from .forms import *
from .models import Consola, TiempoJuego, Precio

#Este código define una vista basada en clase que renderiza una plantilla HTML e incluye información de un modelo TiempoJuego, como el total de horas, minutos, costo de tiempo y control, y costo total.
@method_decorator(login_required(login_url='/login/'),name='dispatch')
class index(ListView):
    template_name = 'managementime/inicio.html'
    model = TiempoJuego

    def get_queryset(self):
        queryset = super().get_queryset().select_related('precio')
        queryset = queryset.filter(fecha_creacion__date = datetime.now())
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_horas = context['object_list'].aggregate(total_horas=Sum('horas'))['total_horas']
        total_minutos = context['object_list'].aggregate(total_minutos=Sum('minutos'))['total_minutos']
        costo_tiempo = context['object_list'].aggregate(costo_tiempo=Sum('precio__costo_tiempo'))['costo_tiempo']
        costo_control = context['object_list'].aggregate(costo_control=Sum('precio__costo_control'))['costo_control']
        control_extra = context['object_list'].aggregate(control_extra=Sum('control_extra'))['control_extra']
        if costo_tiempo:
            costo_total = costo_tiempo + costo_control
        else:
            total_horas = 0
            total_minutos = 0
            costo_tiempo = 0
            costo_control = 0
            control_extra = 0
            costo_total = 0
        context.update({
            'total_horas': total_horas,
            'total_minutos': total_minutos,
            'costo_tiempo': costo_tiempo,
            'costo_control': costo_control,
            'costo_total': costo_total,
            'control_extra': control_extra,
        })
        return context

@method_decorator(login_required(login_url='/login/'),name='dispatch')
class TiempoJuegoCreateView(CreateView):
    template_name = 'managementime/tiempojuego_form.html'
    model = TiempoJuego
    form_class = TiempoJuegoForm
    success_url = '/lista/'

    def form_valid(self, form):
        """
        Obtener la instancia de TiempoJuego a partir del formulario.
        """
        tiempo_juego = form.save(commit=False)
        
        """
        Este código obtiene la hora actual y la asigna al campo "hora_inicio" de una instancia de TiempoJuego.
        """
        now = datetime.now()
        hora_inicio = time(hour=now.hour, minute=now.minute, second=now.second)
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
            delta = timedelta(hours=tiempo_juego.horas, minutes=tiempo_juego.minutos)
            hora_fin = (datetime.combine(date.today(), hora_inicio) + delta).time()
            tiempo_juego.hora_fin = hora_fin
        elif tiempo_juego.hora_fin is not None: 
            hora_fin = tiempo_juego.hora_fin
            datetime1 = datetime.datetime.combine(date.today(), hora_inicio)    
            datetime2 = datetime.datetime.combine(date.today(), hora_fin)
            hora_fin = datetime2 - datetime1
            tiempo_juego.horas = hora_fin.seconds // 3600
            tiempo_juego.minutos = (hora_fin.seconds // 60) % 60
        else:
            tiempo_juego.horas = 0
            tiempo_juego.minutos = 0 
            tiempo_juego.hora_fin = datetime.time(hour=0, minute=0, second=0)
        
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
        costo_tiempo = (horasc * 60 + minutosc) * 50
        costo_total = costo_control + costo_tiempo
        
        precio = Precio()
        precio.costo_control = costo_control
        precio.costo_tiempo = costo_tiempo
        precio.costo_total = costo_total
        
        precio.tiempo_juego = tiempo_juego
        precio.save()
        messages.success(self.request,'Creado correctamente')
        
        return super().form_valid(form)

@method_decorator(login_required(login_url='/login/'),name='dispatch')
class TiempoJuegoUpdateView(UpdateView):
    template_name = 'managementime/tiempojuego_form.html'
    model = TiempoJuego
    form_class = TiempoJuegoForm
    success_url = '/lista/'

    def form_valid(self, form):
        """
        Obtener la instancia de TiempoJuego a partir del formulario.
        """
        tiempo_juego = form.save(commit=False)
        
        """
        Este fragmento verifica si se proporcionaron las horas y los minutos para calcular la hora de finalización 
        y si es así, lo calcula.
        Si no se proporcionaron las horas y los minutos pero se proporcionó la hora de finalización,
        calcula la duración y actualiza las horas y minutos. 
        Si no se proporcionó ni la hora de finalización ni las horas y minutos, 
        establece la hora de finalización en 00:00:00 y las horas y minutos en 0.
        """
        if 'horas' in form.changed_data or 'minutos' in form.changed_data:
            # El usuario cambió la cantidad de horas o minutos, por lo que necesitamos recalcular la hora de finalización
            hora_inicio = tiempo_juego.hora_inicio
            if tiempo_juego.horas is not None and tiempo_juego.minutos is not None:
                delta = timedelta(hours=tiempo_juego.horas, minutes=tiempo_juego.minutos)
                hora_fin = (datetime.combine(date.today(), hora_inicio) + delta).time()
                tiempo_juego.hora_fin = hora_fin
            else:
                # Si no se proporcionaron las horas y los minutos, establecemos la hora de finalización en 00:00:00 y las horas y minutos en 0.
                tiempo_juego.horas = 0
                tiempo_juego.minutos = 0 
                tiempo_juego.hora_fin = datetime.time(hour=0, minute=0, second=0)
        
        
        if 'hora_fin' in form.changed_data:
            hora_inicio = tiempo_juego.hora_inicio
            hora_fin = tiempo_juego.hora_fin
            if hora_inicio and hora_fin:
                tiempo_jugado = datetime.combine(date.today(), hora_fin) - datetime.combine(date.today(), hora_inicio)
                tiempo_juego.horas = tiempo_jugado.seconds // 3600
                tiempo_juego.minutos = (tiempo_jugado.seconds // 60) % 60
                precio = Precio.objects.first()  # Obtener el objeto Precio correspondiente
                precio_total = precio.costo_tiempo * tiempo_juego.horas  # Calcular el precio total
                tiempo_juego.precio_total = precio_total  # Actualizar el precio total en el objeto TiempoJuego
            else:
                tiempo_juego.horas = None
                tiempo_juego.minutos = None
                tiempo_juego.precio_total = None
        
        precio = tiempo_juego.precio
        control_extra = form.cleaned_data['control_extra']
        if control_extra is not None:
            costo_control = control_extra * 500
        horasc = tiempo_juego.horas
        minutosc = tiempo_juego.minutos
        costo_tiempo = (horasc * 60 + minutosc) * 50
        costo_total = costo_control + costo_tiempo
                
        precio.costo_control = costo_control
        precio.costo_tiempo = costo_tiempo
        precio.costo_total = costo_total
        precio.save()
            
        tiempo_juego.save()
        messages.success(self.request,'Modificado correctamente')
        return super().form_valid(form)

@method_decorator(login_required(login_url='/login/'),name='dispatch')
class TiempoJuegoListView(ListView):
    model = TiempoJuego
    template_name = 'managementime/ver_tiempos_de_juego.html'
    context_object_name = 'TiempoJuegoList'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(fecha_creacion__date = datetime.now())
        queryset = queryset.annotate(
            costo_control=F('precio__costo_control'),
            costo_tiempo=F('precio__costo_tiempo'),
            costo_total=F('precio__costo_total')
        ).order_by('hora_fin')
        return queryset

@login_required
def TiempoJuegoDeleteView(request, pk):
    usuario = get_object_or_404(TiempoJuego, pk=pk)
    usuario.delete()
    return redirect(to='lista')

@method_decorator(login_required(login_url='/login/'),name='dispatch')
class ConsolaCreateView(PermissionRequiredMixin,CreateView):
    model = Consola
    form_class = consolaForm
    permission_required = 'managementime.add_consola'
    template_name = 'managementime/consola_form.html'
    success_url = '/ver-consola/'
    
@method_decorator(login_required(login_url='/login/'),name='dispatch')
class VerConsolaListView(ListView):
    model = Consola
    template_name = 'managementime/ver_consola.html'
    context_object_name = 'VerConsolaList'

@login_required
@permission_required('managementime.delete_consola')
def ConsolaDeleteView(request, pk):
    usuario = get_object_or_404(Consola, pk=pk)
    usuario.delete()
    return redirect(to='ver_consolas')

@method_decorator(login_required(login_url='/login/'),name='dispatch')
class ConsolaUpdateView(PermissionRequiredMixin,UpdateView):
    template_name = 'managementime/consola_form.html'
    model = Consola
    form_class = consolaForm
    permission_required = 'managementime.update_consola'
    success_url = '/ver-consola/'

    def form_valid(self, form):
        Consola.save
        messages.success(self.request,'modificado correctamente')
        return super().form_valid(form)

@method_decorator(login_required(login_url='/login/'),name='dispatch')
class RegistrosPorRangoFechasView(TemplateView):
    template_name = 'managementime/registros_por_rango_fechas.html'
    form_class = ReporteForm
    
    def get_queryset(self):
        queryset = TiempoJuego.objects.filter(fecha_creacion__date=timezone.now())
        queryset = queryset.annotate(
            costo_control=F('precio__costo_control'),
            costo_tiempo=F('precio__costo_tiempo'),
            costo_total=F('precio__costo_total'),
            precio_id=F('precio__id')
        ).select_related('precio').order_by('hora_fin')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET or None)
        context['registros'] = []

        if self.request.GET and context['form'].is_valid():
            fecha_inicial = context['form'].cleaned_data['fecha_inicial']
            fecha_final = context['form'].cleaned_data['fecha_final']
            registros = TiempoJuego.objects.filter(fecha_creacion__range=(fecha_inicial, fecha_final)).select_related('precio')

            # Agregar precios a cada registro
            for registro in registros:
                registro.costo_control = registro.precio.costo_control
                registro.costo_tiempo = registro.precio.costo_tiempo
                registro.costo_total = registro.precio.costo_total
                registro.precio_id = registro.precio.id

            context['registros'] = registros

        # Calcular el total de costo
            total_costo = registros.aggregate(total=Sum('precio__costo_total'))['total']
            context['total_costo'] = total_costo

        return context

#autenticacion de usuraios
class CustomLoginView(LoginView):
    template_name = 'managementime/login.html'

    def get_success_url(self):
        return reverse_lazy('inicio')

#Registro de usuarios nuevos
@method_decorator(login_required(login_url='/login/'),name='dispatch')
class SignUpView(PermissionRequiredMixin,CreateView):
    form_class = CustomUserCreationForm
    permission_required = 'managementime.add_user'
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@method_decorator(login_required(login_url='/login/'),name='dispatch')
class TerminosView(TemplateView):
    template_name = "managementime/terminos.html"
