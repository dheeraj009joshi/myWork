
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
scouter=ScouterPlaces("new") #using "new" to use the new db urls use "old" for the old db 
scouter.get_proxies_urls()

# try :
scouter.Update_current_popilarity_24_7(CITY_DATA["ATLANTA"]["ID"]) # run this function in a infinite loop 
# data=scouter.get_place_info_from_google("Our Bar ATL atlanta","","")
# print(data)
# except Exception as e:
#     print(e)
#     print("hiiiiii")
#     pass