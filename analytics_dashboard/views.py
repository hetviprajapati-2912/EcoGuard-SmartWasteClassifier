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
    # Get filter from query parameter
    filter_option = request.GET.get('filter', 'month')

    # Load sample/mock data
    dates = pd.date_range(end=pd.Timestamp.today(), periods=90)
    df = pd.DataFrame({
        'date': dates,
        'transport': np.random.randint(1, 10, len(dates)),
        'electricity': np.random.randint(1, 10, len(dates)),
        'food': np.random.randint(1, 10, len(dates)),
        'plastic': np.random.randint(1, 10, len(dates)),
    })

    # Force last 5 rows to have today's date
    df.loc[df.tail(5).index, 'date'] = pd.Timestamp.today().normalize()

    # Total CO₂ column
    df['co2'] = df[['transport', 'electricity', 'food', 'plastic']].sum(axis=1)
    df['date'] = pd.to_datetime(df['date'])

    # Filtering
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

    # Line Chart for CO₂ Emissions
    fig = px.line(df_filtered, x='date', y='co2', title=f'CO₂ Emissions - {filter_option.capitalize()} View')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(255,255,255,0.5)')
    graph_html = fig.to_html(full_html=False)


    # Radar Chart: User avg vs Global avg
    categories = ['Transport', 'Electricity', 'Food', 'Plastic']
    user_avg = df_filtered[['transport', 'electricity', 'food', 'plastic']].mean()
    global_avg = pd.Series([6, 7, 5, 4], index=categories)  # Mock global avg

    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(r=user_avg.values, theta=categories, fill='toself', name='User'))
    radar_fig.add_trace(go.Scatterpolar(r=global_avg.values, theta=categories, fill='toself', name='Global'))
    radar_fig.update_layout(title='Radar Comparison: User vs Global Averages', polar=dict(bgcolor='rgba(255,255,255,0.1)'), paper_bgcolor='rgba(240,248,255,1)')
    radar_html = radar_fig.to_html(full_html=False)

    # Grouped Bar Chart: CO₂ by category
    bar_df = df_filtered.groupby(df_filtered['date'].dt.date)[['transport', 'electricity', 'food', 'plastic']].sum().reset_index()

    bar_fig = go.Figure()
    for cat in categories:
        bar_fig.add_trace(go.Bar(x=bar_df['date'], y=bar_df[cat.lower()], name=cat))
    bar_fig.update_layout(barmode='group', title='Category-wise CO₂ Emissions Over Time', paper_bgcolor='rgba(248,255,248,0.8)')
    bar_html = bar_fig.to_html(full_html=False)

    # Waterfall Chart: Weekly change
    weekly_df = df.set_index('date').resample('W').sum().reset_index()
    weekly_df['change'] = weekly_df['co2'].diff().fillna(0)
    waterfall_fig = go.Figure(go.Waterfall(
        x=weekly_df['date'].dt.strftime('%Y-%m-%d'),
        y=weekly_df['change'],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    waterfall_fig.update_layout(title="CO₂ Emission Changes Week by Week", paper_bgcolor='rgba(250,250,255,0.9)')
    waterfall_html = waterfall_fig.to_html(full_html=False)

    # ✅ Streak Chart
    streak_html = generate_streak_chart(df)

    # Pass all graphs to dashboard
    return render(request, 'analytics_dashboard/dashboard.html', {
        'graph_html': graph_html,
        'radar_html': radar_html,
        'bar_html': bar_html,
        'waterfall_html': waterfall_html,
        'streak_html': streak_html  # ✅ Included here
    })

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
