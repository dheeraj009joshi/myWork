import geonamescache
from geopy.geocoders import Nominatim

def get_cities_by_country(country_name):
    gc = geonamescache.GeonamesCache()
    cities = gc.get_cities()
    
    # Initialize geolocator
    geolocator = Nominatim(user_agent="geo_locator")
    
    city_list = []
    
    for city_id, city_info in cities.items():
        if city_info['countrycode'] and city_info['countrycode'].lower() in gc.get_countries():
            country_full_name = gc.get_countries()[city_info['countrycode']]['name']
            if country_full_name.lower() == country_name.lower():
                location = geolocator.geocode(city_info['name'] + ", " + country_full_name)
                if location:
                    city_list.append({
                        "city": city_info['name'],
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    })
    
    return city_list

# Example usage
# country = input("Enter a country name: ")
cities = get_cities_by_country("IS")

if cities:
    for city in cities:
        print(f"City: {city['city']}, Latitude: {city['latitude']}, Longitude: {city['longitude']}")
else:
    print("No cities found or incorrect country name.")
