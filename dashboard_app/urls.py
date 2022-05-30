from django.contrib import admin
from django.urls import path
from .views import (

    DashboardHome,



)

urlpatterns = [

    path('', DashboardHome.as_view() ,name='Dashboard'),


]