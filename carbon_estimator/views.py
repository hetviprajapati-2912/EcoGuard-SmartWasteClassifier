from django.shortcuts import render, redirect
from .models import CarbonEntry
from .forms import CarbonEntryForm
from .utils import get_impact_rating, detect_outliers_zscore, get_personalized_tip, get_achievement_badges
from django.db.models import Avg
import matplotlib.pyplot as plt
import seaborn as sns
import os
import io
import base64
from matplotlib.dates import DateFormatter
from datetime import date

def carbon_dashboard(request):
    form = CarbonEntryForm()
    message = ''
    chart = None
    outliers = []
    tip = ''
    rating = ''
    badges = []

    if request.method == 'POST':
        form = CarbonEntryForm(request.POST)
        if form.is_valid():
            # Save or update today's entry
            today = date.today()
            entry, created = CarbonEntry.objects.update_or_create(
                date=today,
                defaults=form.cleaned_data
            )
            total_emission = entry.calculate_emissions()
            message = f"Your CO₂ emission today is {total_emission} kg CO₂e"
            rating = get_impact_rating(total_emission)
            tip = get_personalized_tip(entry)
            badges = get_achievement_badges(total_emission)

    # Get all entries ordered by date for trend
    entries = CarbonEntry.objects.all().order_by('date')
    dates = [e.date for e in entries]
    emissions = [e.calculate_emissions() for e in entries]

    # Detect outliers
    if emissions:
        outliers = detect_outliers_zscore(emissions)

        plt.switch_backend('Agg')
        fig, ax = plt.subplots(figsize=(10, 6)) 

        ax.plot(dates, emissions, marker='o')
        ax.set_title('CO₂ Emission Trend')
        ax.set_ylabel('kg CO₂e')
        ax.xaxis.set_major_formatter(DateFormatter("%d-%b"))
        fig.autofmt_xdate()

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_png = buf.getvalue()
        buf.close()
        chart = base64.b64encode(image_png).decode('utf-8')

    # Get today's entry for summary and category-wise emissions
    today_entry = CarbonEntry.objects.filter(date=date.today()).first()
    if today_entry:
        total_emission_today = today_entry.calculate_emissions()
        rating_today = get_impact_rating(total_emission_today)
        today_category_emissions = {
            'Transport': round(today_entry.transport_km * 0.12, 2),
            'Electricity': round(today_entry.electricity_kwh * 0.92, 2),
            'Food': {
                'veg': 2.0,
                'non-veg': 7.0,
                'mixed': 4.5
            }.get(today_entry.food_type.lower(), 3.0),
            'Plastic': round(today_entry.plastic_grams * 0.0088, 2),
        }
    else:
        total_emission_today = 0
        rating_today = 'No data'
        today_category_emissions = {}

    # Prepare data for trend chart (last 7 days)
    last_7_entries = CarbonEntry.objects.order_by('-date')[:7]
    last_7_entries = list(reversed(last_7_entries))  # chronological order
    trend_dates = [e.date.strftime('%a') for e in last_7_entries]
    trend_values = [e.calculate_emissions() for e in last_7_entries]

    # Radar chart user values — today's category emissions or zeroes
    radar_user_values = [
        today_category_emissions.get('Transport', 0),
        today_category_emissions.get('Electricity', 0),
        today_category_emissions.get('Food', 0),
        today_category_emissions.get('Plastic', 0),
    ]

    # You can calculate weekly goal progress dynamically or keep it static here
    weekly_goal_progress = 65

    # Prepare personalized tips list
    tips = [
        tip,
        "Try a vegetarian meal tomorrow – it could save 3kg of CO₂",
        "Reduce electricity usage by switching off unused devices",
        "Use public transport more often",
    ] if tip else [
        "Try a vegetarian meal tomorrow – it could save 3kg of CO₂",
        "Reduce electricity usage by switching off unused devices",
        "Use public transport more often",
    ]

    context = {
        'form': form,
        'message': message,
        'chart': chart,

        'todays_rating': rating_today,
        'total_emission': total_emission_today,
        'global_comparison': 'Below Global Average',

        'categories': ['Transport', 'Electricity', 'Food', 'Plastic'],
        'emissions_values': radar_user_values,

        'trend_dates': trend_dates or ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'trend_values': trend_values or [11, 12, 10, 14, 13, 15, 12],

        'radar_categories': ['Transport', 'Electricity', 'Food', 'Plastic'],
        'radar_user_values': radar_user_values,
        'radar_family_values': [4, 3.5, 3, 1.2],  # Example static family data

        'weekly_goal_progress': weekly_goal_progress,

        'tips': tips,
        'badges': badges,
        'rating': rating,
        'outliers': outliers,
    }
    return render(request, 'carbon_estimator/dashboard.html', context)