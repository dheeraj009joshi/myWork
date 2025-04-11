
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA

#
scouter=ScouterPlaces("new") #using "new" to use the new db urls use "old" for the old db 


try :
    scouter.Update_current_popilarity_24_7(CITY_DATA["HYDERABAD"]["ID"]) # run this function in a infinite loop 
    
except:
    print("hiiiiii")
    pass