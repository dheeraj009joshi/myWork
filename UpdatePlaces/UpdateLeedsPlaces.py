import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA

scouter=ScouterPlaces("new")

places=scouter.get_places_data(CITY_DATA["LEEDS"]["ID"])
scouter.get_proxies_urls()
# scouter.update_places(places,CITY_DATA["LEEDS"]["ID"],"Dec 22 2024")
scouter.update_places(places, "Leeds")
