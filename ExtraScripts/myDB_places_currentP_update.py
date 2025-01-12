import sys
import requests as re
import os
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")
from scouter.PlaceClass import ScouterPlaces
from scouter.config import CITY_DATA

# Initialize ScouterPlaces
scouter = ScouterPlaces("old")  # Use "new" for new DB URLs, "old" for old DB
scouter.get_proxies_urls()
places = re.get("http://localhost:3000/api/places").json()["data"]

def met(place_data):
    """Update the current popularity of a place."""
    # try:
        # Fetch popularity info from Google
    up = scouter.get_place_info_from_google(place_data["GooglePlaceName"], "leeds", "")

    # Prepare URL and payload
    url = f"http://localhost:3000/api/places/{place_data['_id']}"  # Adjust base URL
    headers = {"Content-Type": "application/json"}
    payload = {"currentPopularity": up["CurrentPopularity"]}
    print(payload)
    # Make PUT request
    response = re.put(url, json=payload, headers=headers)
    print(response.content)
    response_data = response.json()

    if response.status_code == 200:
        print(f"Place {place_data['_id']} updated successfully: {response_data['message']}")
    else:
        print(f"Failed to update place {place_data['_id']}: {response_data.get('message', 'Unknown error')}")
    # except Exception as e:
    #     print(f"An error occurred for place {place_data['_id']}: {str(e)}")

# Process each place in a thread
for i in places:
    thread = threading.Thread(target=met, args=(i,))  # Pass `i` as a tuple
    thread.start()
    thread.join()  # Optional: Wait for the thread to finish
