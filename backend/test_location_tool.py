from geopy.geocoders import Nominatim
import requests

geolocator = Nominatim(user_agent="safespace-ai-therapist")

def find_nearby_therapists_by_location(location: str) -> str:
    # Step 1: Location ko lat/lng mein convert karna
    geocode_result = geolocator.geocode(location)
    
    if not geocode_result:
        return "Location not found"
    
    lat, lng = geocode_result.latitude, geocode_result.longitude
    print(lat, lng)
    
    # Step 2: Overpass API se nearby therapists/clinics dhoondna
    radius = 5000  # meters
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["healthcare"="psychotherapist"](around:{radius},{lat},{lng});
      node["amenity"="doctors"]["healthcare:speciality"~"psychotherapy|psychiatry"](around:{radius},{lat},{lng});
      node["amenity"="clinic"](around:{radius},{lat},{lng});
    );
    out body;
    """
    
    headers = {"User-Agent": "safespace-ai-therapist"}
    
    try:
        response = requests.get(overpass_url, params={"data": overpass_query}, headers=headers, timeout=30)
        response.raise_for_status()  # agar server error ho (500, 429 etc) to yahan exception aayega
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error contacting Overpass API: {e}"
    except ValueError:
        return "Overpass API server busy or returned invalid response. Please try again in a moment."
    
    elements = data.get("elements", [])
    
    if not elements:
        return f"No nearby therapists found near {location}"
    
    output = [f"Therapists near {location}:"]
    top_results = elements[:5]
    
    for place in top_results:
        tags = place.get("tags", {})
        name = tags.get("name", "Unknown")
        address_parts = [
            tags.get("addr:street", ""),
            tags.get("addr:housenumber", ""),
            tags.get("addr:city", "")
        ]
        address = " ".join(p for p in address_parts if p) or "Address not available"
        phone = tags.get("phone", tags.get("contact:phone", "Phone not available"))
        
        output.append(f"- {name} | {address} | {phone}")
    
    result = "\n".join(output)
    print(result)
    return result

find_nearby_therapists_by_location(location="Berlin")