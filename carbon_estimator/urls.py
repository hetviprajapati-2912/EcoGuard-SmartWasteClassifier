from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.carbon_dashboard, name='carbon_dashboard'),
    
]
