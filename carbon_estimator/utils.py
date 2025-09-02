import numpy as np

def get_impact_rating(total_emission):
    if total_emission < 5:
        return "🟢 Low Impact"
    elif total_emission < 15:
        return "🟡 Moderate Impact"
    else:
        return "🔴 High Impact"

def detect_outliers_zscore(data):
    if len(data) < 2:
        return []
    mean = np.mean(data)
    std = np.std(data)
    return [i for i in data if abs((i - mean) / std) > 2]

def get_personalized_tip(entry):
    tips = []
    if entry.food_type == "non-veg":
        tips.append("🌿 Try a vegetarian meal tomorrow – it could save 3kg of CO₂")
    if entry.electricity_kwh > 10:
        tips.append("💡 Turn off unused appliances to reduce power consumption")
    if entry.plastic_grams > 100:
        tips.append("♻️ Reduce plastic use – try cloth bags or reusable containers")
    if entry.transport_km > 20:
        tips.append("🚲 Consider biking or public transport to lower emissions")
    return tips or ["✅ You're doing great! Keep it up."]

def get_achievement_badges(total_emission):
    badges = []
    if total_emission < 10:
        badges.append("🟢 Eco Starter")
    if total_emission < 7:
        badges.append("🔋 Power Saver")
    if total_emission < 6 and 'veg' in str(total_emission).lower():
        badges.append("🌿 Veg Hero")
    return badges
