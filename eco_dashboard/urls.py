from django.urls import path
from . import views

urlpatterns = [
    path('', views.eco_dashboard_view, name='eco_dashboard'),

]
