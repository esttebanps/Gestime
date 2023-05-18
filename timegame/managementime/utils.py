from django import forms
from django.db.models import Sum
import datetime as dt, time
from datetime import date, timedelta, datetime
from .models import GameTime, Price

#CONSTANTES
EXTRA_CONTROLLER_COST = 500
TIME_COST_PER_MINUTE = 50

#FUNCIONES
def calculate_end_time(game_time, start_time):
        if game_time.hours is not None and game_time.minutes is not None:
            delta = timedelta(hours=game_time.hours, minutes=game_time.minutes)
            end_time = (datetime.combine(date.today(), start_time) + delta).time()
            game_time.end_time = end_time
        elif game_time.end_time is not None: 
            end_time = game_time.end_time
            datetime1 = datetime.combine(date.today(), start_time)    
            datetime2 = datetime.combine(date.today(), end_time)
            end_time = datetime2 - datetime1
            game_time.hours = end_time.seconds // 3600
            game_time.minutes = (end_time.seconds // 60) % 60
        else:
            game_time.hours = 0
            game_time.minutes = 0 
            game_time.end_time = time(hour=0, minute=0, second=0)

def calculate_price(game_time, extra_controller):
    if extra_controller is not None:
        controller_cost = extra_controller * EXTRA_CONTROLLER_COST
    else:
        controller_cost = 0
    
    hoursc = game_time.hours
    minutesc = game_time.minutes
    time_cost = (hoursc * 60 + minutesc) * TIME_COST_PER_MINUTE
    total_cost = controller_cost + time_cost
    
    if game_time.pk is None:
        game_time.save()
        
    price, created = Price.objects.get_or_create(game_time=game_time)
    price.controller_cost = controller_cost
    price.time_cost = time_cost
    price.total_cost = total_cost
    price.save()
    
    return price
def process_game_time(game_time, extra_controller):
    now = datetime.now()
    start_time = dt.time(hour=now.hour, minute=now.minute, second=now.second)
    game_time.start_time = start_time
    calculate_end_time(game_time, start_time)
    calculate_price(game_time, extra_controller)
    
def update_game_time(game_time, changed_data, cleaned_data):
    if 'hours' in changed_data or 'minutes' in changed_data:
        start_time = game_time.start_time
        calculate_end_time(game_time, start_time)
    
    if 'end_time' in changed_data:
        start_time = game_time.start_time
        end_time = game_time.end_time
        if start_time and end_time:
            played_time = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
            game_time.hours = played_time.seconds // 3600
            game_time.minutes = (played_time.seconds // 60) % 60
            price = Price.objects.get(game_time=game_time)
            total_price = price.time_cost * game_time.hours  
            game_time.total_price = total_price  
        else:
            game_time.hours = None
            game_time.minutes = None
            game_time.total_price = None
    
    extra_controller = cleaned_data['extra_controller']
    price = calculate_price(game_time, extra_controller)
    game_time.save()
