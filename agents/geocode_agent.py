import requests

def get_coordinates(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1,
        "accept-language": "en"
    }
    res = requests.get(url, params=params, headers={"User-Agent": "InkleTourApp/1.0"})
    data = res.json()
    if not data:
        return None
    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    display_name = data[0]["display_name"]
    map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=14/{lat}/{lon}"
    return {
        "lat": lat,
        "lon": lon,
        "display_name": display_name,
        "map_url": map_url
    }
