from datetime import datetime
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.EventsClass import ScouterEvents
from scouter.config import CITY_DATA

scouter=ScouterEvents("new")

places=scouter.get_all_events_for_city(CITY_DATA["LONDON"]["ID"],CITY_DATA["LONDON"]["COUNTRY"],CITY_DATA["LONDON"]["EVENT_ID"])
