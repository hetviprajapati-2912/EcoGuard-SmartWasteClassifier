from django.urls import path
from . import views
from . import views_enhanced

urlpatterns = [
    path('', views_enhanced.dashboard_view, name='dashboard'),
    path('api/data/', views_enhanced.get_dashboard_data, name='dashboard_api'),
    path('map/', views.map_view, name='map_view'),
]