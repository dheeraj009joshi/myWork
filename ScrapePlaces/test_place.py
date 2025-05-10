import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA


scouter=ScouterPlaces("new")
scouter.get_proxies_urls()

scouter.insert_all_places_for_city("b386f4d6-4444-4ff9-b95c-db697cd8487a","Jaipur","India")