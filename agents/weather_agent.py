import requests

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "precipitation_probability",
        "timezone": "auto"
    }
    res = requests.get(url, params=params)
    data = res.json()
    if "current_weather" in data:
        weather = data["current_weather"]
        rain_prob = data["hourly"]["precipitation_probability"][0] if "hourly" in data and "precipitation_probability" in data["hourly"] else 0
        return {
            "temperature": weather["temperature"],
            "windspeed": weather["windspeed"],
            "description": f"{weather['weathercode']}", # decode code if you like
            "rain_chance": rain_prob
        }
    return None

def get_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto"
    }
    res = requests.get(url, params=params)
    data = res.json()
    forecast = []
    if "daily" in data:
        days = data["daily"]["time"]
        temps_max = data["daily"]["temperature_2m_max"]
        temps_min = data["daily"]["temperature_2m_min"]
        rains = data["daily"]["precipitation_probability_max"]
        for i in range(len(days)):
            forecast.append({
                "date": days[i],
                "temp_max": temps_max[i],
                "temp_min": temps_min[i],
                "rain_chance": rains[i]
            })
    return forecast
