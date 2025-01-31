


import json
import time
import requests
from .PlaceClass import ScouterPlaces

class ScouterEvents:
    def __init__(self,db):
        self.headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzE5LzIwMjQgMTI6MTU6MDUiLCJuYmYiOjE3MzIwMTg1MDUsImV4cCI6MTc2MzU1NDUwNSwiaWF0IjoxNzMyMDE4NTA1fQ.C3hycswaAgRvhEFesttElyq2CYI0uvqa9Y1nimar3hk"
        }
        self.BASE_URL = "https://portal.maiden-ai.com"
        self.PLACE_CLASS=ScouterPlaces("new")
        self.ptoxies=self.PLACE_CLASS.get_proxies_urls()
        # self.procies=
        
    
    def get_place_id(self,data,CITY_ID,COUNTRY):
    
        place_id=""
        aa=self.PLACE_CLASS.get_place_info_from_google(data["primary_venue"]["name"]+" "+data["primary_venue"]['address']["localized_address_display"],CITY_ID,COUNTRY)
        # print(aa) 
        if aa== None:
            aa=self.PLACE_CLASS.get_place_info_from_google(data["primary_venue"]['name'],CITY_ID,COUNTRY)
            
        filter_data={"filterInfo": [
                {
                "filterTerm":aa["PlaceName"],
                "filterType": "EQUALS",
                "filterBy": "PlaceName"
                }
                ]
            }

        main=requests.post(f"{self.BASE_URL}/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/Place/list",json=filter_data,headers=self.headers).json()
        print(main)
        if main["total"]>0:
            print(" place  found ")
            place_id=main["data"][0]['PlaceId']
            print(place_id)
        else:
            print(" place not found inserting place ")
            aa=self.PLACE_CLASS.insert_place(data["primary_venue"]["name"]+" "+data["primary_venue"]['address']["localized_address_display"],data["primary_venue"]['address']["localized_address_display"],CITY_ID,data["primary_venue"]['address']['city'],COUNTRY)
            print(aa)
            place_id=aa['result']
        

        return place_id
    
    
    def _request_to_get_events(self,page,places):
    # print(page)
        url = "https://www.eventbrite.com/api/v3/destination/search/"
        headers2 = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "cookie": "csrftoken=2e3538a6c9824469a685b83c7958d595; ebEventToTrack=; eblang=lo%3Den_US%26la%3Den-us; AN=; location=%7B%22current_place_parent%22%3A%20%22India%22%2C%20%22place_type%22%3A%20%22locality%22%2C%20%22current_place%22%3A%20%22R%5Cu016bpnagar%22%2C%20%22latitude%22%3A%2030.9695%2C%20%22country%22%3A%20%22India%22%2C%20%22place_id%22%3A%20%22102028795%22%2C%20%22slug%22%3A%20%22india--rupnagar%22%2C%20%22longitude%22%3A%2076.5324%7D; G=v%3D2%26i%3D76f71af8-f5d2-47ec-be2f-46e051ffb752%26a%3D1358%26s%3D5632eef8fc39081560764385e44963262290d93a; django_timezone=Asia/Calcutta; SS=AE3DLHQE2MjsYtYZhONljcTK0iOvi9AWiw; AS=6d3dbf12-aea0-45ad-9241-d80d98f8b382; location={%22current_place_parent%22:%22India%22,%22place_type%22:%22locality%22,%22current_place%22:%22Jaipur%22,%22latitude%22:26.9525,%22country%22:%22India%22,%22place_id%22:%22102030017%22,%22slug%22:%22india--jaipur%22,%22longitude%22:75.7105}; mgrefby=; mgaff1049793750367=ebdssbdestsearch; mgref=eafil; stableId=828b12dc-5570-45b3-8492-6ed5e09d82c3; SP=AGQgbbmSMiBvgJpsxY1Ra1v5l_kjrpu04YxahhFek6JYH8bgwAY6aPLtbTQHEzK3yF8i-UaRrDyFNZyiw-8fJ3o1QEsur3oLL3-e0aP-ItTTKMfzmb7MZazGnZwsiajfiE7ffe_r4EdNG-ECsUy2sv_pz6CuOotSYrYGByn_bpJBKQU1ZoJQmJj1da4myEkJ_d6UVirlUIvUCRo2cE0qvNgJt_IcIF8RwZ7EFKRo_vn1DmBSNHyu7eI; _dd_s=rum=0&expire=1732376467110",
            "origin": "https://www.eventbrite.com",
            "priority": "u=1, i",
            "referer": "https://www.eventbrite.com/d/united-kingdom--leeds/all-events/?page=2",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "x-csrftoken": "2e3538a6c9824469a685b83c7958d595",
            "x-requested-with": "XMLHttpRequest",
        }

        data = {
            "event_search": {
                "dates": "current_future",
                "dedup": True,
                "places": places,#["101750367"], 
                "tags": ["EventbriteFormat/11"],
                "page": page,
                "page_size": 20,
                "online_events_only": False,
            },
            "expand.destination_event": [
                "primary_venue",
                "image",
                "ticket_availability",
                "saves",
                "event_sales_status",
                "primary_organizer",
                "public_collections",
            ],
            "browse_surface": "search",
        }
        # print(data)
        time.sleep(0.010)
        # Make the request
        response = requests.post(url, headers=headers2, json=data)
        # Output the response
        # print(response.status_code)
        print(response.json())
        return response.json()


    def get_all_events_for_city(self,CITY_ID,COUNTRY,Events_Places_Id):
        for i in range(1,50):
            res = self._request_to_get_events(i + 1,Events_Places_Id)
            if res["events"]["results"] ==[]:
                break
            for d in res["events"]["results"]:
                try:
                    da = json.loads(json.dumps(d))
                    # print(d)
                    hashtags = [t["display_name"] for t in da["tags"]]
                    try:
                        hashtag1 = hashtags[0]
                    except:
                        hashtag1 = ""
                    try:
                        hashtag2 = hashtags[1]
                    except:
                        hashtag2 = ""
                    try:
                        hashtag3 = hashtags[2]
                    except:
                        hashtag3 = ""
                    try:
                        hashtag4 = hashtags[3]
                    except:
                        hashtag4 = ""
                    try:
                        hashtag5 = hashtags[4]
                    except:
                        hashtag5 = ""

                    try:
                        start_time = f"{d['start_date']}T{d['start_time']}:00"
                        end_time = f"{d['end_date']}T{d['end_time']}:00"
                    except:
                        start_time = f"{d['start_date']}T{d['start_time']}:00"
                        end_time = f"{d['start_date']}T{d['end_time']}:00"  # when end's on same day
                        
                    
                        
                    # handel getting place scraping it and in not added will add it 
                    
                    placeid=self.get_place_id(d,CITY_ID,COUNTRY)



                    reqjsn={
                        "ActivityType": "Event",
                        "AttachmentType": "Image",
                        "Title": d["name"],
                        "Description": d["summary"],
                        "MigratedUrl": d["image"]["url"],
                        "Hashtag1": hashtag1,
                        "Hashtag2": hashtag2,
                        "Hashtag3": hashtag3,
                        "Hashtag3": hashtag4,
                        "Hashtag3": hashtag5,
                        # "BatchName": "Batch_11-23-2024",
                        "StartTime": start_time,
                        "EndTIme": end_time,
                        "Latitude": d["primary_venue"]['address']["latitude"],
                        "Longitude": d["primary_venue"]['address']["longitude"],
                        "Address": d["primary_venue"]['address']["localized_address_display"],
                        "CityId": CITY_ID,
                        "PlaceId":placeid,
                        "Url":d["url"],
                        "Emoji":"1F4C5",
                        "MinimumTicketPrice":d["ticket_availability"]["minimum_ticket_price"]["major_value"],
                        "MaximumTicketPrice":d["ticket_availability"]["maximum_ticket_price"]["major_value"],
                        "Currency":d["ticket_availability"]["maximum_ticket_price"]["currency"],
                        "TicketsUrl ":d["tickets_url"],
                        "IsSoldOut":d["ticket_availability"]["is_sold_out"],
                        "FullDescription":d["full_description"]
                    }
                    if reqjsn["FullDescription"]==None:
                        reqjsn.pop("FullDescription")
                    print(reqjsn)
                    res = requests.post(
                        f"{self.BASE_URL}/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/Activity/insert",
                        json=reqjsn,
                        headers=self.headers,
                    ).json()
                    print(res)
                    
                except:
                    pass
