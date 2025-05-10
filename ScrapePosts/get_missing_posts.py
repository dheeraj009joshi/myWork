from datetime import datetime
import sys
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scouter.PostClass import GetPosts
from scouter.config import PROD_URLS, CITY_DATA

current_date = datetime.now().strftime("%b %d %Y")
scouter = GetPosts("new")

def check_place_activity(place):
    place_id = place["PlaceId"]
    data = {
        "filterInfo": [
            {
                "filterTerm": place_id,
                "filterType": "EQUALS",
                "filterBy": "PlaceId"
            }
        ],
        "pageSize": 100000
    }
    try:
        res = requests.post(
            PROD_URLS["BASE_URL"] + "/" + PROD_URLS["ACTIVITY_LIST"],
            json=data,
            headers=scouter.headers,
            timeout=10
        ).json()
        print(res)
        if res.get("total", 0) == 0:
            return place
    except Exception as e:
        print(f"Error fetching activity for PlaceId {place_id}: {e}")
    return None

# try:
    # scouter.notify_actions_to_admin(f"Update :- Post Extraction started with Batch :- {current_date} :)")
    
places = scouter.get_all_non_selected_city_places()[:10]
print(len(places))
new_places = []

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(check_place_activity, place) for place in places]
    for future in as_completed(futures):
        result = future.result()
        if result:
            new_places.append(result)

# Now test location posts for all places
print(len(new_places))
scouter.get_the_posts(new_places)

# except Exception as error:
#     print(error)
    # scouter.notify_actions_to_admin(
    #     f"Error :- Post Extraction with Batch :- {current_date} got error :- {error} :)"
    # )
