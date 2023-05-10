from datetime import *
from django.db import models
from django.forms import ValidationError
class Console(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
class GameTime(models.Model):
    console = models.ForeignKey(Console,null=True, on_delete=models.SET_NULL)
    hours = models.IntegerField(blank=True, null=True)
    minutes = models.IntegerField(blank=True, null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(blank=True, null=True)
    extra_controller = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    is_active = models.BooleanField()

    
    
class Price(models.Model):
    game_time = models.OneToOneField(GameTime, on_delete=models.CASCADE)
    controller_cost = models.IntegerField(default=0)
    time_cost = models.IntegerField(default=0)
    total_cost = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)