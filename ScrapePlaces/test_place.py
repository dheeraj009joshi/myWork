import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA


scouter=ScouterPlaces("new")
scouter.get_proxies_urls()
aa=scouter.insert_place("Crag House Farm Otley ","Old Rd, Cookridge, Leeds LS16 7NH, United Kingdom","","","UK")