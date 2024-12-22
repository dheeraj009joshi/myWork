import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA


scouter=ScouterPlaces("old")