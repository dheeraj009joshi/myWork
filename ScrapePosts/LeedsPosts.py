from datetime import datetime
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PostClass import GetPosts
from scouter.config import CITY_DATA

scouter=GetPosts("new")
places=scouter.get_places_data(CITY_DATA["LEEDS"]["ID"])
current_date = datetime.now().strftime("%b %d %Y")

scouter.test_location_posts(places,CITY_DATA["LEEDS"]["ID"],current_date)

