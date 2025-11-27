from django.contrib import admin
from django.urls import path
from .views import weather_api
urlpatterns = [

    path('weather/<str:location>/',weather_api),

]
