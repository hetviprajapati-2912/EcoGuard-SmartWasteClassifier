from django.db import models
from datetime import date

class CarbonEntry(models.Model):
    date = models.DateField(default=date.today)
    transport_km = models.FloatField()
    electricity_kwh = models.FloatField()
    food_type = models.CharField(max_length=20)  # 'veg', 'non-veg', 'mixed'
    plastic_grams = models.FloatField(default=0.0)  # Newly added field

    def calculate_emissions(self):
        transport_emission = self.transport_km * 0.12       # per km
        electricity_emission = self.electricity_kwh * 0.92  # per kWh
        food_emission = {
            'veg': 2.0,
            'non-veg': 7.0,
            'mixed': 4.5
        }.get(self.food_type.lower(), 3.0)
        plastic_emission = self.plastic_grams * 0.0088  # Assume 8.8g CO2e per gram plastic, example

        return round(transport_emission + electricity_emission + food_emission + plastic_emission, 2)
