import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA


scouter=ScouterPlaces("new")
scouter.get_proxies_urls()
aa=scouter.extract_insta_url("Platinum Lace London | Piccadilly Circus 13 Coventry St, Piccadilly, London W1D 7DH, United Kingdom ")

print(aa)