import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA


scouter=ScouterPlaces("old")

places=scouter.get_places_data("723289d5-9983-4a2f-6538-08dcc857d3e1")
ii=1
for i in places:
    if i["PlaceId"]=="adf9094f-0426-492f-af9f-08dd0ecffaa7":
        break
    ii+=1
print(ii)