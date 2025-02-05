from datetime import datetime
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PostClass import GetPosts
from scouter.config import CITY_DATA
# from scouter.utils import places

current_date = datetime.now().strftime("%b %d %Y")

scouter=GetPosts("new")
try:
    scouter.notify_actions_to_admin(f'''Update :- Post Extraction started  with Batch :- {current_date} :)''')
    places=scouter.get_places_data(CITY_DATA["LONDON"]["ID"])

    scouter.test_location_posts(places,CITY_DATA["LONDON"]["ID"],current_date)
except Exception as error :
    scouter.notify_actions_to_admin(f'''Error :- Post Extraction   with Batch :- {current_date} got error :- {error}:)''')
