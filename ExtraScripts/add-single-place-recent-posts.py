import sys
import os

import requests 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("hii")

from scouter.PostClass import GetPosts
from scouter.config import CITY_DATA,mobile_urls
scouter=GetPosts("old")

data={
        "filterInfo": [
            {
            "filterTerm":"Neighbourhood Leeds",
            "filterType": "EQUALS",
            "filterBy": "PlaceName"
            }
            ],
        "pageSize": 100000 
        }
        

main=requests.post(mobile_urls['BASE_URL']+mobile_urls["PLACE_LIST"],json=data).json()
scouter.test_location_posts(main['data'],CITY_DATA["LEEDS"]["ID"],"Dec 17 2024")