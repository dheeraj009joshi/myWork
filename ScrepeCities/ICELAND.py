from datetime import datetime
import sys
import os
import concurrent.futures
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces

scouter=ScouterPlaces("new")
country="IS"
cities=scouter.get_cities_by_country(country)
print(cities)
def get_single_city_data_with_places(city_data):
    print(f"Task started for {city_data['CityName']}")
    city_id = scouter.get_city_id(city_data)  # Might not work with multiprocessing if scouter isn't picklable
    if city_id:
        print(f"City ID for {city_data['CityName']}: {city_id}")
        scouter.insert_all_places_for_city(city_id, city_data["CityName"], city_data["Country"])
        print(f"Task completed for {city_data['CityName']}")
    else:
        print(f"Failed to get city ID for {city_data['CityName']}")

# if __name__ == "__main__":
#     with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
#         executor.map(get_single_city_data_with_places, cities)


for city_data in cities:
    get_single_city_data_with_places(city_data)