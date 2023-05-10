# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core import serializers
from django.core.mail import send_mail
from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    )
from django.views.generic.edit import FormView, UpdateView
from .forms import *
from .models import Console, GameTime, Price
from .utils import *

# Python imports
import datetime
import json
from itertools import chain
from requests import request
from datetime import datetime, date, time, timedelta

@method_decorator(login_required(login_url='/login/'), name='dispatch')
class index(ListView):
    template_name = 'managementime/inicio.html'
    model = GameTime

    def get_queryset(self):
        queryset = super().get_queryset().select_related('price')
        queryset = queryset.filter(created_time__date=datetime.now())
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hours_total = context['object_list'].aggregate(hours_total=Sum('hours'))['hours_total']
        minutes_total = context['object_list'].aggregate(minutes_total=Sum('minutes'))['minutes_total']
        time_cost = context['object_list'].aggregate(time_cost=Sum('price__time_cost'))['time_cost']
        controller_cost = context['object_list'].aggregate(controller_cost=Sum('price__controller_cost'))['controller_cost']
        extra_controller = context['object_list'].aggregate(extra_controller=Sum('extra_controller'))['extra_controller']

        # Sumar los minutos a las horas cuando los minutos superan los 60
        if minutes_total:
            hours_total += minutes_total // 60
            minutes_total = minutes_total % 60

        if time_cost:
            total_cost = time_cost + controller_cost
        else:
            hours_total = 0
            minutes_total = 0
            time_cost = 0
            controller_cost = 0
            extra_controller = 0
            total_cost = 0

        context.update({
            'hours_total': hours_total,
            'minutes_total': minutes_total,
            'time_cost': time_cost,
            'controller_cost': controller_cost,
            'total_cost': total_cost,
            'extra_controller': extra_controller,
        })
        return context
class GameTimeCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new GameTime instance.
    """
    login_url = reverse_lazy('login')
    template_name = 'managementime/tiempojuego_form.html'
    model = GameTime
    form_class = GameTimeForm
    success_url = reverse_lazy('lista')

    def form_valid(self, form):
        """
        Process the form and save the new GameTime instance.
        """
        
        game_time = form.save(commit=False)
        extra_controller = form.cleaned_data['extra_controller']
        process_game_time(game_time, extra_controller)
        messages.success(self.request,'La operación se ha completado con éxito.')
        return super().form_valid(form)
class GameTimeUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    template_name = 'managementime/tiempojuego_form.html'
    model = GameTime
    form_class = GameTimeForm
    success_url = '/lista/'

    def form_valid(self, form):
        game_time = form.save(commit=False)
        update_game_time(game_time,form.changed_data, form.cleaned_data)
        messages.success(self.request,'Los cambios se han guardado exitosamente.')
        return super().form_valid(form)
class GameTimeListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = GameTime
    template_name = 'managementime/ver_tiempos_de_juego.html'
    context_object_name = 'GameTimeList'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(created_time__date = datetime.now())
        queryset = queryset.annotate(
            controller_cost=F('price__controller_cost'),
            time_cost=F('price__time_cost'),
            total_cost=F('price__total_cost')
        ).order_by('end_time')
        return queryset
@login_required
@permission_required('managementime.delete_gametime')
def GameTimeDeleteView(request, pk):
    game_time = get_object_or_404(GameTime, pk=pk)
    game_time.delete()
    return redirect(to='lista')
class ConsoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = '/login/'
    model = Console
    form_class = ConsoleForm
    permission_required = 'managementime.add_console'
    template_name = 'managementime/consola_form.html'
    success_url = '/ver-consola/'
class ConsoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = '/login/'
    template_name = 'managementime/consola_form.html'
    model = Console
    form_class = ConsoleForm
    permission_required = 'managementime.update_console'
    success_url = '/ver-consola/'

    def form_valid(self, form):
        Console.save
        messages.success(self.request,'Modificado correctamente')
        return super().form_valid(form)
class ConsoleListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Console
    template_name = 'managementime/ver_consola.html'
    context_object_name = 'ConsoleList'
@login_required
@permission_required('managementime.delete_console')
def ConsoleDeleteView(request, pk):
    console = get_object_or_404(Console, pk=pk)
    console.delete()
    return redirect(to='ver_consolas')
@method_decorator(login_required(login_url='/login/'),name='dispatch')
class DateRangeRecordsView(TemplateView):
    template_name = 'managementime/registros_por_rango_fechas.html'
    form_class = ReportForm
    
    def get_queryset(self):
        queryset = GameTime.objects.filter(created_time__date=timezone.now())
        queryset = queryset.annotate(
            controller_cost=F('price__controller_cost'),
            time_cost=F('price__time_cost'),
            total_cost=F('price__total_cost'),
            price_id=F('price__id')
        ).select_related('price').order_by('end_time')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET or None)
        context['records'] = []

        if self.request.GET and context['form'].is_valid():
            start_date = context['form'].cleaned_data['start_date']
            end_date = context['form'].cleaned_data['end_date']
            console = context['form'].cleaned_data.get('console')
            
            records = GameTime.objects.filter(created_time__range=(start_date, end_date)).select_related('price')

            if console:
                records = records.filter(console=console)
            
            # Agregar precios a cada registro
            for record in records:
                record.controller_cost = record.price.controller_cost
                record.time_cost = record.price.time_cost
                record.total_cost = record.price.total_cost
                record.price_id = record.price.id

            context['records'] = records

        # Calcular el total de costo
            total_cost = records.aggregate(total=Sum('price__total_cost'))['total']
            context['total_cost'] = total_cost

            minutes_hours_total = records.aggregate(total_hours=Sum('hours'), total_minutes=Sum('minutes'))

        # Sumar los minutos adicionales a las horas
            if minutes_hours_total['total_minutes'] is not None:
                extra_hours, minutes = divmod(minutes_hours_total['total_minutes'], 60)
                minutes_hours_total['total_hours'] += extra_hours
                minutes_hours_total['total_minutes'] = minutes
            else:
                minutes_hours_total['total_hours'] = 0
                minutes_hours_total['total_minutes'] = 0
            
            context['total_hours'] = minutes_hours_total['total_hours']
            context['total_minutes'] = minutes_hours_total['total_minutes']
        return context
class CustomLoginView(LoginView):
    template_name = 'managementime/login.html'

    def get_success_url(self):
        return reverse_lazy('inicio')
@method_decorator(login_required(login_url='/login/'),name='dispatch')
class SignUpView(PermissionRequiredMixin,CreateView):
    form_class = CustomUserCreationForm
    permission_required = 'managementime.add_user'
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
@method_decorator(login_required(login_url='/login/'),name='dispatch')
class TermsConditionsView(TemplateView):
    template_name = "managementime/terminos.html"
@method_decorator(login_required(login_url='/login/'),name='dispatch')
class BackupView(View):
    def get(self, request):
        games_times = GameTime.objects.all()
        consoles = Console.objects.all()
        prices = Price.objects.all()

        # Concatenamos los tres conjuntos de objetos en una sola lista
        data = list(chain(games_times, consoles, prices))

        # Serializamos la lista completa
        data = serializers.serialize('json', data)

        # Creamos la respuesta HTTP y la devolvemos
        response = HttpResponse(data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="backup-alpha-gamer.json"'
        return response
@method_decorator(login_required(login_url='/login/'),name='dispatch')
class RestoreView(FormView):
    template_name = 'managementime/restore.html'
    form_class = BackupForm
    success_url = '/restore/'

    def form_valid(self, form):
        backup_file = self.request.FILES['backup_file']
        data = backup_file.read().decode('utf-8')
        try:
            objects = serializers.deserialize('json', data)
            for obj in objects:
                obj.save()
            messages.success(self.request,'Restaurado correctamente')
            return super().form_valid(form)
        except Exception as e:
            error_message = {'message': str(e)}
            return HttpResponseServerError(render_to_string('error500.html', context=error_message))

    def form_invalid(self, form):
        return super().form_invalid(form)
class HelpView(View):
    template_name = 'managementime/ayuda.html'
    success_template_name = 'managementime/contact_success.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Envía el correo electrónico al soporte técnico de la empresa
        send_mail(
            subject,
            f'Nombre: {name}\nCorreo electrónico: {email}\nMensaje: {message}',
            settings.DEFAULT_FROM_EMAIL,
            ['angelesteban0326@gmail.com'],
            fail_silently=False,
        )

        # Renderiza una página de confirmación de envío
        return render(request, self.success_template_name)