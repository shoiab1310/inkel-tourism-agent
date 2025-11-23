import requests

def get_places(lat, lon):
    # Gets up to 5 tourist attractions using Overpass API
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:15];
    (
      node["tourism"="attraction"](around:5000,{lat},{lon});
      way["tourism"="attraction"](around:5000,{lat},{lon});
    );
    out center 5;
    """
    res = requests.post(overpass_url, data=query, headers={"User-Agent": "InkleTourApp/1.0"})
    data = res.json()
    places = []
    count = 0
    for element in data['elements']:
        if 'tags' in element and 'name' in element['tags']:
            # If available, get name and OpenStreetMap URL
            lat_val = element.get('lat', element.get('center', {}).get('lat', lat))
            lon_val = element.get('lon', element.get('center', {}).get('lon', lon))
            places.append({
                "name": element['tags']['name'],
                "osm_url": f"https://www.openstreetmap.org/?mlat={lat_val}&mlon={lon_val}#map=18/{lat_val}/{lon_val}"
            })
            count += 1
            if count == 5:
                break
    return places
