from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import folium
from folium.plugins import MarkerCluster
import json
import random

def dashboard_view(request):
    # Handle AJAX requests for real-time updates
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return get_dashboard_data(request)
    
    # Regular page load
    return render(request, 'analytics_dashboard/dashboard.html', {
        'achievements': get_user_achievements(),
        'ai_insights': get_ai_insights(),
        'streak_data': get_streak_data()
    })

def get_dashboard_data(request):
    """API endpoint for real-time dashboard data"""
    filter_option = request.GET.get('filter', 'month')
    chart_type = request.GET.get('chart_type', 'line')
    
    # Generate sample data
    dates = pd.date_range(end=pd.Timestamp.today(), periods=90)
    df = pd.DataFrame({
        'date': dates,
        'transport': np.random.randint(1, 10, len(dates)),
        'electricity': np.random.randint(1, 10, len(dates)),
        'food': np.random.randint(1, 10, len(dates)),
        'plastic': np.random.randint(1, 10, len(dates)),
    })
    
    df['co2'] = df[['transport', 'electricity', 'food', 'plastic']].sum(axis=1)
    df['date'] = pd.to_datetime(df['date'])
    
    # Apply time filter
    if filter_option == 'day':
        df_filtered = df[df['date'] >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)]
    elif filter_option == 'week':
        df_filtered = df[df['date'] > datetime.now() - timedelta(weeks=1)]
    elif filter_option == 'month':
        df_filtered = df[df['date'] > datetime.now() - timedelta(days=30)]
    elif filter_option == 'quarter':
        df_filtered = df[df['date'] > datetime.now() - timedelta(days=90)]
    elif filter_option == 'year':
        df_filtered = df[df['date'] > datetime.now() - timedelta(days=365)]
    else:
        df_filtered = df
    
    # Prepare data for frontend
    data = {
        'dates': df_filtered['date'].dt.strftime('%Y-%m-%d').tolist(),
        'emissions': df_filtered['co2'].tolist(),
        'transport': df_filtered['transport'].tolist(),
        'electricity': df_filtered['electricity'].tolist(),
        'food': df_filtered['food'].tolist(),
        'plastic': df_filtered['plastic'].tolist(),
        'categories': ['Transport', 'Electricity', 'Food', 'Plastic'],
        'category_totals': [
            df_filtered['transport'].sum(),
            df_filtered['electricity'].sum(),
            df_filtered['food'].sum(),
            df_filtered['plastic'].sum()
        ],
        'radar_user': df_filtered[['transport', 'electricity', 'food', 'plastic']].mean().tolist(),
        'radar_global': [6, 7, 5, 4],
        'achievements': get_user_achievements(),
        'ai_insights': get_ai_insights(),
        'streak_data': get_streak_data()
    }
    
    return JsonResponse(data)

def get_user_achievements():
    """Generate user achievements data"""
    return [
        {'icon': '🌱', 'title': 'Eco Starter', 'description': 'First week of tracking', 'unlocked': True},
        {'icon': '🔥', 'title': '7-Day Streak', 'description': 'Low emissions for a week', 'unlocked': True},
        {'icon': '🌍', 'title': 'Planet Saver', 'description': 'Saved 100kg CO₂', 'unlocked': True},
        {'icon': '⚡', 'title': 'Energy Efficient', 'description': 'Reduced electricity by 20%', 'unlocked': False},
        {'icon': '🚗', 'title': 'Transport Hero', 'description': 'Used public transport 10 times', 'unlocked': False},
        {'icon': '♻️', 'title': 'Recycling Champion', 'description': 'Recycled 50 items', 'unlocked': True}
    ]

def get_ai_insights():
    """Generate AI-powered insights"""
    insights = [
        {
            'icon': '💡',
            'title': 'Smart Recommendation',
            'text': 'Try reducing transport emissions on Mondays - you typically emit 30% more on this day.',
            'type': 'recommendation'
        },
        {
            'icon': '📊',
            'title': 'Pattern Recognition',
            'text': 'Your emissions are 20% higher on weekends. Consider planning eco-friendly weekend activities.',
            'type': 'pattern'
        },
        {
            'icon': '🎯',
            'title': 'Personalized Tip',
            'text': 'You\'re doing great! Your carbon footprint decreased 15% this quarter compared to last.',
            'type': 'tip'
        },
        {
            'icon': '🌳',
            'title': 'Impact Visualization',
            'text': f'You saved equivalent to {random.randint(8, 15)} trees planted this month! Keep up the excellent work.',
            'type': 'impact'
        }
    ]
    return random.sample(insights, 3)  # Return 3 random insights

def get_streak_data():
    """Generate streak tracking data"""
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    streak_data = []
    current_streak = 0
    
    for date in dates:
        is_low_emission = random.choice([True, False, True, True])  # 75% chance of low emission day
        if is_low_emission:
            current_streak += 1
        else:
            current_streak = 0
        
        streak_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'streak': current_streak,
            'is_low_emission': is_low_emission
        })
    
    return {
        'data': streak_data,
        'current_streak': current_streak,
        'best_streak': max([d['streak'] for d in streak_data])
    }

# Map view remains unchanged
def map_view(request):
    data = [
        [28.6139, 77.2090, "Delhi", 120],
        [19.0760, 72.8777, "Mumbai", 95],
        [13.0827, 80.2707, "Chennai", 85],
        [22.5726, 88.3639, "Kolkata", 60],
        [12.9716, 77.5946, "Bangalore", 110],
        [26.9124, 75.7873, "Jaipur", 75]
    ]

    m = folium.Map(location=[22.9734, 78.6569], zoom_start=5)
    marker_cluster = MarkerCluster().add_to(m)

    for lat, lon, city, co2 in data:
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{city}</b><br>CO₂: {co2} kg",
            tooltip=city,
            icon=folium.Icon(color="green" if co2 < 90 else "red")
        ).add_to(marker_cluster)

    map_html = m._repr_html_()
    return render(request, 'analytics_dashboard/map.html', {'map_html': map_html})

def generate_streak_chart(df):
    global_limit = 4.5  # kg CO2 per day (approximate average)
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['total_emissions'] = df[['transport', 'food', 'electricity']].sum(axis=1)
    df['under_limit'] = df['total_emissions'] <= global_limit

    # Calculate streaks
    streak = 0
    streaks = []
    for under in df['under_limit']:
        if under:
            streak += 1
        else:
            streak = 0
        streaks.append(streak)

    df['streak'] = streaks

    # Marker colors
    marker_colors = ['green' if u else 'red' for u in df['under_limit']]

    trace = go.Scatter(
        x=df['date'],
        y=df['streak'],
        mode='lines+markers',
        marker=dict(color=marker_colors, size=10),
        line=dict(color='royalblue', width=2),
        name='Streak'
    )

    layout = go.Layout(
        title='📈 Eco Streak Tracker: Days Under Global CO₂ Limit',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Streak Length'),
        plot_bgcolor='rgba(240,240,255,0.8)',
        paper_bgcolor='white',
        font=dict(size=14)
    )

    fig = go.Figure(data=[trace], layout=layout)
    return fig.to_html(full_html=False)