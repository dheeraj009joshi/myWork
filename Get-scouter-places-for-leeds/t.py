import requests as re

data={
    "filterInfo": [
        {
        "filterTerm":"c118807b-e7a0-4999-efcf-08dab69f5de6",
        "filterType": "EQUALS",
        "filterBy": "cityId"
        },
        
        {"filterTerm": "pub,bar,lounge,club",
        "filterBy": "PlaceType",
        "filterType": "MULTICONTAINS"
        },
        ]
    }
BASE_URL="https://scouterlive.azurewebsites.net"
main=re.post(f"{BASE_URL}/api/v1/Place/List",json=data).json()

googlePlaceName=[]
for i in main["data"]:
    # print(i)
    place_name=i["GooglePlaceName"]
    googlePlaceName.append(place_name)
rows = googlePlaceName
# rows=['park bar atlanta']
print(len(rows))