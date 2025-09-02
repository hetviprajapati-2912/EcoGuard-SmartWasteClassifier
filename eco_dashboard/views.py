from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import random
from django.http import JsonResponse

# 🌱 EcoBot Logic (backend)
@csrf_exempt
def eco_dashboard_view(request):
    chatbot_reply = ""
    aqi_message = ""
    products = [
        {"name": "Bamboo Toothbrush", "link": "https://earthhero.com/products/bamboo-toothbrush", "rating": "⭐ 4.5"},
        {"name": "Reusable Metal Straw Kit", "link": "https://ecosia.org/s/metal-straw-kit", "rating": "⭐ 4.7"},
        {"name": "Eco Reusable Grocery Bags", "link": "https://www.amazon.in/eco-reusable-bags", "rating": "⭐ 4.6"},
    ]

    events = [
        {"name": "🌱 Tree Plantation Drive", "lat": 23.0301, "lng": 72.5803},
        {"name": "🧹 Clean-Up Drive", "lat": 23.0266, "lng": 72.5666},
        {"name": "🏕️ Sustainability Fair", "lat": 23.0359, "lng": 72.5950},
    ]

    if request.method == "POST":
        if "chatInput" in request.POST:
            input_text = request.POST.get("chatInput").lower()

            if "plastic" in input_text:
                chatbot_reply = "♻️ Switch to reusable containers and avoid single-use plastics!"
            elif "solar" in input_text:
                chatbot_reply = "☀️ Solar panels reduce fossil fuel dependence and save energy long-term!"
            elif "water" in input_text:
                chatbot_reply = "💧 Try using low-flow taps and avoid water wastage while brushing!"
            else:
                chatbot_reply = "🌿 Try reducing waste, using public transport, and conserving energy!"

        if "cityInput" in request.POST:
            city = request.POST.get("cityInput")
            aqi = random.randint(50, 200)
            if aqi > 150:
                aqi_message = f"⚠️ AQI in {city} is {aqi}. Try to stay indoors and avoid pollution."
            else:
                aqi_message = f"✅ AQI in {city} is {aqi}. Air quality is moderate."

    context = {
        "chatbot_reply": chatbot_reply,
        "aqi_message": aqi_message,
        "products": products,
        "events": events,
    }

    return render(request, "eco_dashboard/dashboard.html", context)
