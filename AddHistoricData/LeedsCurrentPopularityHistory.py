
import sys
import os
import time 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
scouter=ScouterPlaces("new") #using "new" to use the new db urls use "old" for the old db 

while True:
    try :
        scouter.History_current_popilarity_24_7(CITY_DATA["LEEDS"]["ID"]) # run this function in a infinite loop 
        time.sleep(90)
    except:
        print("hiiiiii")
        pass