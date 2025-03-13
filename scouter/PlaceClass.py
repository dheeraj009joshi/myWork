
from datetime import datetime, timedelta
import time
import requests
from .utils import zipcodes,user_agent_list,user_agents_for_reviews
import json
import logging
import random
import re
import ssl
from urllib.parse import quote
from .config import ALLOWED_CATEGORIES, PROXIES_SEARCH_URL1,PROXIES_SEARCH_URL2,PROXIES_SEARCH_URL3,PROD_URLS,mobile_urls
from hikerapi import Client
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys
import urllib.request


class ScouterPlaces:
    
    def __init__(self,DB):
        self.db=DB
        if DB=="old":
            self.BASE_URLS=mobile_urls
        else:
            self.BASE_URLS=PROD_URLS
        self.cl=Client("0daja8wqtv3o16jpszpj582tbyduul3t")
        self.proxies=[]
        
        self.headers= {
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NzNhZWViYS00Y2FlLTRjODktYjhlZS05OWYzNDFiYTM2NmMiLCJVc2VySWQiOiI3NzNhZWViYS00Y2FlLTRjODktYjhlZS05OWYzNDFiYTM2NmMiLCJEZXZpY2VJZCI6IjUzNzM4ODBGLTkwN0UtNDc4NS04MjZELUUyRUZDREVCNzc0RCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjEyLzI4LzIwMjQgMTg6Mzc6MzciLCJuYmYiOjE3MzU0MTEwNTcsImV4cCI6MTc2Njk0NzA1NywiaWF0IjoxNzM1NDExMDU3fQ.1HQWE1HYZy08MTT7YOCuLDTQtz_8ZxM6MzCZpBWhs9I"
    }
        
    def get_proxies_urls(self):
        urls = []
        for search_url in [PROXIES_SEARCH_URL1,PROXIES_SEARCH_URL2,PROXIES_SEARCH_URL3]:
            try:
                resp = urllib.request.urlopen(urllib.request.Request(url=search_url, data=None))
                data = resp.read().decode('utf-8').split('/*""*/')[0]
                urls.extend(data.split("\n"))
            except Exception as e:
                print(f"Error fetching from {search_url}: {e}")
        print(len(urls))
        self.proxies=urls
        return urls

        # return urls

    def get_place_info_from_google(self,placename,CITY_ID,COUNTRY):
        # try:
            address = quote(placename).split()
            user_agent = random.choice(user_agent_list)
            headers = {'User-Agent': user_agent}
            def get_popularity_for_day(popularity):
                """
                Returns popularity for day
                :param popularity:
                :return:
                """

                # Initialize empty matrix with 0s
                pop_json = [[0 for _ in range(24)] for _ in range(7)]
                wait_json = [[0 for _ in range(24)] for _ in range(7)]
                if not popularity:
                    return ["",
                            "",
                            "",
                            "",
                            "",
                            "",
                            ""],['null','null','null','null','null','null','null']

                for day in popularity:

                    day_no, pop_times = day[:2]

                    if pop_times:
                        for hour_info in pop_times:

                            hour = hour_info[0]
                            pop_json[day_no - 1][hour] = hour_info[1]

                            # check if the waiting string is available and convert no minutes
                            if len(hour_info) > 5:
                                wait_digits = re.findall(r'\d+', hour_info[3])

                                if len(wait_digits) == 0:
                                    wait_json[day_no - 1][hour] = 0
                                elif "min" in hour_info[3]:
                                    wait_json[day_no - 1][hour] = int(wait_digits[0])
                                elif "hour" in hour_info[3]:
                                    wait_json[day_no - 1][hour] = int(wait_digits[0]) * 60
                                else:
                                    wait_json[day_no - 1][hour] = int(wait_digits[0]) * 60 + int(wait_digits[1])

                            # day wrap
                            if hour_info[0] == 23:
                                day_no = day_no % 7 + 1

                ret_popularity = [
                    {
                        "data": pop_json[d]
                    } for d in range(7)
                ]
                popularity = []
                for pops in ret_popularity:
                    strs = str(pops["data"]).strip('[]')
                    popularity.append(strs)
                if len(popularity) == 0:
                    popularity=['0','0','0','0','0','0','0']

                # waiting time only if applicable
                ret_wait = [{
                        "data": wait_json[d]
                    } for d in range(7)
                ] if any(any(day) for day in wait_json) else []
                timewait = []
                for pops in ret_wait:
                    strs = str(pops["data"]).strip('[]')
                    timewait.append( strs)
                if len(timewait) == 0:
                    timewait=['null','null','null','null','null','null','null']
                # {"name" : "monday", "data": [...]} for each weekday as list
                return popularity, timewait
            def index_get(array, *argv):
                try:
                    for index in argv:
                        array = array[index]
                    return array
                except (IndexError, TypeError):
                    return None
            
            
            
            def convert_time(time_str):
                if "am" in time_str.lower():
                    return time_str.lower().replace("am", "")
                elif "pm" in time_str.lower():
                    hours, minutes = map(int, time_str.lower().replace("pm", "").split(":") if ":" in time_str else (time_str.lower().replace("pm", ""), "0"))
                    return f"{hours + 12 if hours != 12 else 12}:{minutes:02d}" if ":" in time_str else str(hours + 12 if hours != 12 else 12)
                return time_str  # In case the string is already in 24-hour format

            def extract_openingtiming(i,start_index,end_index):
                d=str(i[1][0]).replace("\u202f","").split("–")
                print(d)
                if len(d) == 1 and d[0] == "Closed":
                    start="0"
                    end="0"
                else:
                    start = convert_time(d[0])
                    end = convert_time(d[-1])

                OpeningHour.insert(start_index,start)
                OpeningHour.insert(end_index,end)
            
            params_url = {
                    "tbm": "map",
                    "tch": 1,
                    "hl": "en",
                    "q":"+".join(address).replace(" ",""),
                    "pb": "!4m12!1m3!1d4005.9771522653964!2d-122.42072974863942!3d37.8077459796541!2m3!1f0!2f0!3f0!3m2!1i1125!2i976"
                        "!4f13.1!7i20!10b1!12m6!2m3!5m1!6e2!20e3!10b1!16b1!19m3!2m2!1i392!2i106!20m61!2m2!1i203!2i100!3m2!2i4!5b1"
                        "!6m6!1m2!1i86!2i86!1m2!1i408!2i200!7m46!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!"
                        "1m3!1e4!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e"
                        "10!2b0!3e4!2b1!4b1!9b0!22m6!1sa9fVWea_MsX8adX8j8AE%3A1!2zMWk6Mix0OjExODg3LGU6MSxwOmE5ZlZXZWFfTXNYOGFkWDh"
                        "qOEFFOjE!7e81!12e3!17sa9fVWea_MsX8adX8j8AE%3A564!18e15!24m15!2b1!5m4!2b1!3b1!5b1!6b1!10m1!8e3!17b1!24b1!"
                        "25b1!26b1!30m1!2b1!36b1!26m3!2m2!1i80!2i92!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i976!1m6!1m2!1i1075!2i0!2m2!"
                        "1i1125!2i976!1m6!1m2!1i0!2i0!2m2!1i1125!2i20!1m6!1m2!1i0!2i956!2m2!1i1125!2i976!37m1!1e81!42b1!47m0!49m1"
                        "!3b1"
                }

            search_url = "https://www.google.de/search?" + "&".join(k + "=" + str(v) for k, v in params_url.items())
            # search_url="https://www.google.de/search?" + "&"+"tbm"+"="+"map"+"&"+"tch"+"="+"1"+"&"+"hl"+"="+"en"+"&"+"q"+"="+urllib.quote_plus(" ".join(address))+"&"+"pb"+"="+"!4m12!1m3!1d4005.9771522653964!2d-122.42072974863942!3d37.8077459796541!2m3!1f0!2f0!3f0!3m2!1i1125!2i976""!4f13.1!7i20!10b1!12m6!2m3!5m1!6e2!20e3!10b1!16b1!19m3!2m2!1i392!2i106!20m61!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i200!7m46!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e4!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m6!1sa9fVWea_MsX8adX8j8AE%3A1!2zMWk6Mix0OjExODg3LGU6MSxwOmE5ZlZXZWFfTXNYOGFkWDhqOEFFOjE!7e81!12e3!17sa9fVWea_MsX8adX8j8AE%3A564!18e15!24m15!2b1!5m4!2b1!3b1!5b1!6b1!10m1!8e3!17b1!24b1!25b1!26b1!30m1!2b1!36b1!26m3!2m2!1i80!2i92!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i976!1m6!1m2!1i1075!2i0!2m2!1i1125!2i976!1m6!1m2!1i0!2i0!2m2!1i1125!2i20!1m6!1m2!1i0!2i956!2m2!1i1125!2i976!37m1!1e81!42b1!47m0!49m1!3b1"
            logging.info("searchterm: " + search_url)

            url = search_url
            # page = re.get(url, proxies={'http': random.choice(urls)})['ip']
            # print(page)
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            proxy_handler = urllib.request.ProxyHandler({'http': random.choice(self.proxies)})
            req = urllib.request.Request(url=search_url, data=None, headers=headers)
            opener = urllib.request.build_opener(proxy_handler)
            resp = opener.open(req)
            data = resp.read().decode('utf-8').split('/*""*/')[0]
            # f=io.open("data.txt","w",encoding='utf8')  
            # f.write(data)
            jend = data.rfind("}")
            if jend >= 0:
                data = data[:jend + 1]

            jdata = json.loads(data)["d"]
            jdata = json.loads(jdata[4:])

            info = index_get(jdata, 0, 1, 0, 14)
            # ff=open("index.txt","w",encoding="utf-8")   # uncomment to store the response in a file to review that 
            # ff.write(str(info))
            rating = index_get(info, 4, 7)
            rating_n = index_get(info, 4, 8)
            popular_times = index_get(info, 84, 0)
            current_popularity = index_get(info, 84, 7, 1)
            current_popularity_status = index_get(info, 84, 6) or ""
            # print(current_popularity_status)
            time_spent = index_get(info, 117, 0)
            if time_spent:

                nums = [float(f) for f in re.findall(r'\d*\.\d+|\d+', time_spent.replace(",", "."))]
                contains_min, contains_hour = "min" in time_spent, "hour" in time_spent or "hr" in time_spent

                time_spent = None

                if contains_min and contains_hour:
                    time_spent = [nums[0], nums[1] * 60]
                elif contains_hour:
                    time_spent = [nums[0] * 60, (nums[0] if len(nums) == 1 else nums[1]) * 60]
                elif contains_min:
                    time_spent = [nums[0], nums[0] if len(nums) == 1 else nums[1]]

                time_spent = [int(t) for t in time_spent]
                
            def extract_opening_hours(data):
                result = {}
                for entry in data:
                    day = entry[0]
                    time_intervals = entry[-2]  # Directly using time data from entry[-2]

                    if not time_intervals:  # Closed all day
                        result[day] = []
                    else:
                        intervals = []
                        for interval in time_intervals:
                            print(interval)
                            start_time = f"{interval[0]}:{interval[1]}"  # (hour, minute) for start time
                            end_time = f"{interval[2]}:{interval[3]}"  # (hour, minute) for end time
                            intervals.append(start_time)
                            intervals.append(end_time)

                        result[day] = intervals  if intervals!=[] else ["0","0"]
                result_string = "-".join(
                    ",".join(result[day]) if result[day] else "0,0"
                    for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                )
                return result_string



            # a=open("info_27.txt","w",encoding="utf-8") # uncoment to save the response in file to review 
            # a.write(str(index_get(info)))
            populartimes, timewait = get_popularity_for_day(popular_times)
            rating = json.dumps(rating or None)
            rating_n = json.dumps(rating_n or None)
            current_popularity = json.dumps(current_popularity or 0)
            time_spent  = str(time_spent or []).strip('[]')
            priceRange = len(str(index_get(info, 4, 2) or '$'))
            types = index_get(info, 13, 0) or ''
            address = index_get(info, 18) or ""
            description = index_get(info, 32,1,1) or ""
            print(description)
            
            tel = index_get(info, 3, 0) or index_get(info, 178, 0, 0) or ""
            lat = index_get(info, 9, 2) or 0
            lng = index_get(info, 9, 3) or 0
            img=(index_get(info, 72,0,1,6,0)) 
            googleMapLocation = index_get(info, 42) or ""
            try:
                googleImages =",".join( [index_get(img_data, 6,0) for img_data in index_get(info, 52,0,0,14) ])
                print(googleImages)
            except:
                googleImages=img
            try:
                print(index_get(info, 34,1))
                OpeningHour= extract_opening_hours(index_get(info, 34,1)) or ""
                print(OpeningHour)
            except:
                OpeningHour=None
            try:
                review_text_= [i[1] for i in index_get(info, 31,1) ]
                review_text = ",".join(review_text_)
                print(review_text)
            except:
                review_text=""
            facebookLink = index_get(info, 7, 0) or ""
            placeName = index_get(info, 11) or ""
            timeZone = index_get(info, 30) or ""
            neighborhood = index_get(info,14) or ""
            vibe = index_get(info,100)
            avgTimeSpent = index_get(info,117,0) or ""
            zipcode = 0

            for strs in address.replace(',',"").split(" "):
                try:
                    if zipcodes.count(int(strs)) > 0:
                        zipcode = int(strs)
                except:
                    continue
            if priceRange == 4:
                priceRange = '$$$$'
            elif priceRange == 3:
                priceRange = '$$$'
            elif priceRange == 2:
                priceRange = '$$'
            else:
                priceRange = '$'

            
            reviews_list_id=index_get(info,10) or ""
            # print(reviews_list_id)

                
            df={
            "CityId": CITY_ID,
            "PlaceName": placeName,
            "Country": COUNTRY,
            "Address":  address.replace(f"{placeName}, ",''),
            "Zipcode": zipcode,
            "Latitude": lat,
            "Longitude": lng,
            "PlaceType":types,
            "Reviews":review_text,
            "Description":description,
            "BusyHoursSun": populartimes[0].replace(" ",""),
            "BusyHoursMon": populartimes[1].replace(" ",""),
            "BusyHoursTue":populartimes[2].replace(" ",""),
            "BusyHoursWed": populartimes[3].replace(" ",""),
            "BusyHoursThu": populartimes[4].replace(" ",""),
            "BusyHoursFri":populartimes[5].replace(" ",""),
            "BusyHoursSat": populartimes[6].replace(" ",""),
            "OpeningHours":OpeningHour,
            "RaceWhite": 20,
            "RaceBlack": 20,
            "RaceAsian": 20,
            "RaceLatino": 20,
            "RaceIndian": 20,
            "GenderMale": 45,
            "GenderFemale": 45,
            "GenderOthers": 10,
            "InterestGay": 15,
            "InterestStraight": 70,
            "InterestBisexual": 15,
            "PriceRange":priceRange,
            "PhoneNumber": tel,
            "GooglePlaceName": address.replace(f"{placeName},",placeName),
            "GooglePlaceImage":googleImages,
            "Rating": rating,
            "Rating_n": rating_n,
            "ReviewsID":reviews_list_id,
            "CurrentPopularity": current_popularity,
            "CurrentPopularityStatus": current_popularity_status,
            "TimeSpent": time_spent,
            "GoogleMapLocation":  googleMapLocation.replace("1e1","1d1"),
            "FacebookLink": facebookLink.replace("/url?q=",""),
            "TimeZone": timeZone,
            "Neighborhood": neighborhood,
            "AverageTimeSpent":avgTimeSpent,
            }
            
            
            return df
        # except:
        #     print("exception occer")
        #     return None
            
    def insert_place(self,placename,address,CITY_ID,CITY,COUNTRY):
        data=self.get_place_info_from_google(placename,CITY_ID,COUNTRY)
        if data!=None:
            
            if data["PlaceName"]!="" and data['PlaceType'] in ALLOWED_CATEGORIES:
                print("getting images and all")
                print(data)
                try:
                    aa=self.cl.fbsearch_places_v1(placename,data['Latitude'],data["Longitude"])[0]["pk"]
                    data["InstagramLocation"]=aa
                    data["MigratedImages"]=self.get_top3_posts_for_place(aa)
                except:
                    data["InstagramLocation"]=""
                    data["MigratedImages"]=data["GooglePlaceImage"]
                data["InstagramHandle"]=self.extract_insta_url(data['GooglePlaceName']+" insta")
                print(data)
                res=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS['PLACE_INSERT'],json=data,headers=self.headers).json()
                print(res)
                return res
            elif data["PlaceName"]!="":
                data=self.get_place_info_from_google(placename.replace(address,"")+" "+CITY+" "+COUNTRY,CITY_ID,COUNTRY)
                if data["PlaceName"]!="" and data['PlaceType'] in ALLOWED_CATEGORIES:
                    print("getting images and all")
                    try:
                        aa=self.cl.fbsearch_places_v1(placename,data['Latitude'],data["Longitude"])[0]["pk"]
                        data["InstagramLocation"]=aa
                        data["MigratedImages"]=self.get_top3_posts_for_place(aa)
                    except:
                        data["InstagramLocation"]=""
                        data["MigratedImages"]=data["GooglePlaceImage"]
                    data["InstagramHandle"]=self.extract_insta_url(data['PlaceName']+""+ CITY+" insta")
                    print(data)
                    res=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS['PLACE_INSERT'],json=data,headers=self.headers).json()
                    print(res)
                    return res
      
      
    def get_city_id(self,city_data):
    
        filter_data={"filterInfo": [
                {
                "filterTerm":city_data["CityName"],
                "filterType": "EQUALS",
                "filterBy": "CityName"
                },
                {
                "filterTerm":city_data["Country"],
                "filterType": "EQUALS",
                "filterBy": "Country"
                }
                ]
            }
        headers=headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzE5LzIwMjQgMTI6MTU6MDUiLCJuYmYiOjE3MzIwMTg1MDUsImV4cCI6MTc2MzU1NDUwNSwiaWF0IjoxNzMyMDE4NTA1fQ.C3hycswaAgRvhEFesttElyq2CYI0uvqa9Y1nimar3hk"
        }
        
        main=requests.post(f"https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/City/list",json=filter_data,headers=headers).json()
        print(main)
        if main["total"]>0:
            print(" city  found ")
            city_id=main["data"][0]['CityId']
            print(city_id)
        else:
            print(" city  not found inserting city ")
            
            headers=headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzE5LzIwMjQgMTI6MTU6MDUiLCJuYmYiOjE3MzIwMTg1MDUsImV4cCI6MTc2MzU1NDUwNSwiaWF0IjoxNzMyMDE4NTA1fQ.C3hycswaAgRvhEFesttElyq2CYI0uvqa9Y1nimar3hk"
            }
            main=requests.post(f"https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/City/insert",json=city_data,headers=headers).json()
            print(main)  
            city_id=main['result']
            

        return city_id
                
    def extract_coordinates_from_url(self,url: str) -> tuple[float,float]:
        """helper function to extract coordinates from url"""
        
        coordinates = url.split('/@')[-1].split('/')[0]
        # return latitude, longitude
        return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])
      
    @dataclass
    class Business:
        """holds business data"""

        name: str = None
        address: str = None
        img: str = None
        website: str = None
        phone_number: str = None
        reviews_count: int = None
        reviews_average: float = None
        latitude: float = None
        longitude: float = None 
      
    @dataclass
    class BusinessList :
        """holds list of Business objects,
        and save to both excel and csv
        """
        business_list: list['ScouterPlaces.Business'] = field(default_factory=list)
        save_at = 'output'

        def dataframe(self):
            """transform business_list to pandas dataframe

            Returns: pandas dataframe
            """
            return pd.json_normalize(
                (asdict(business) for business in self.business_list), sep="_"
            )

    

        def save_to_csv(self, filename):
            """saves pandas dataframe to csv file

            Args:
                filename (str): filename
            """

            if not os.path.exists(self.save_at):
                os.makedirs(self.save_at)
            self.dataframe().to_csv(f"output/{filename}.csv", index=False)      
            
    def insert_all_places_for_city(self,CITY_ID,CITY,COUNTRY):
    
    ########
    # input 
    ########
    
        # read search from arguments
        self.get_proxies_urls()
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--search", type=str)
        parser.add_argument("-t", "--total", type=int)
        args = parser.parse_args()
        
        if args.search:
            search_list = [args.search]
            
        if args.total:
            total = args.total
        else:
            # if no total is passed, we set the value to random big number
            total = 1000000 # change according to you 

        if not args.search:
            search_list = ALLOWED_CATEGORIES
            # read search from input.txt file
            # input_file_name = 'input.txt'
            # # Get the absolute path of the file in the current working directory
            # input_file_path = os.path.join(os.getcwd(), input_file_name)
            # # Check if the file exists
            # if os.path.exists(input_file_path):
            # # Open the file in read mode
            #     with open(input_file_path, 'r') as file:
            #     # Read all lines into a list
            #         search_list = file.readlines()
                    
            # if len(search_list) == 0:
            #     print('Error occured: You must either pass the -s search argument, or add searches to input.txt')
            #     sys.exit()
            
        ###########
        # scraping
        ###########
        with sync_playwright() as p:
            
            
            for search_for_index, search_for in enumerate(search_list):
                try:
                    browser = p.chromium.launch(headless=False)
                    page = browser.new_page()

                    page.goto("https://www.google.com/maps", timeout=60000)
                    # wait is added for dev phase. can remove it in production
                    page.wait_for_timeout(5000)
                    print(f"-----\n{search_for_index} - {search_for}".strip())

                    page.locator('//input[@id="searchboxinput"]').fill(search_for+" "+CITY+" "+COUNTRY)
                    page.wait_for_timeout(3000)

                    page.keyboard.press("Enter")
                    page.wait_for_timeout(5000)

                    # scrolling
                    page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

                    # this variable is used to detect if the bot
                    # scraped the same number of listings in the previous iteration
                    previously_counted = 0
                    while True:
                        page.mouse.wheel(0, 200000)
                        page.wait_for_timeout(3000)

                        if (
                            page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count()
                            >= total
                        ):
                            listings = page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).all()[:total]
                            # print(listings)
                            # listings = [listing.locator("xpath=..") for listing in listings]
                            # print(listings[0].get_attribute("aria-label"))
                            print(f"Total Scraped: {len(listings)}")
                            break
                        else:
                            # logic to break from loop to not run infinitely
                            # in case arrived at all available listings
                            if (
                                page.locator(
                                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                                ).count()
                                == previously_counted
                            ):
                                listings = page.locator(
                                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                                ).all()
                                print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                                break
                            else:
                                previously_counted = page.locator(
                                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                                ).count()
                                print(
                                    f"Currently Scraped: ",
                                    page.locator(
                                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                                    ).count(),
                                )

                    business_list = ScouterPlaces.BusinessList()
                

                # scraping
                    for listing in listings:
                        try:
                            listing.click()
                            page.wait_for_timeout(2000)

                            name_attibute = 'aria-label'
                            address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                            website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                            phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                            review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                            reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'
                            
                            
                            business = ScouterPlaces.Business()
                        
                            if len(listing.get_attribute(name_attibute)) >= 1:
                
                                business.name = listing.get_attribute(name_attibute).replace("· Visited link","")
                            else:
                                business.name = ""
                            if page.locator(address_xpath).count() > 0:
                                business.address = page.locator(address_xpath).all()[0].inner_text()
                            else:
                                business.address = ""
                            if page.locator(website_xpath).count() > 0:
                                business.website = page.locator(website_xpath).all()[0].inner_text()
                            else:
                                business.website = ""
                            if page.locator(phone_number_xpath).count() > 0:
                                business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                            else:
                                business.phone_number = ""
                            if page.locator(review_count_xpath).count() > 0:
                                business.reviews_count = int(
                                    page.locator(review_count_xpath).inner_text()
                                    .split()[0]
                                    .replace(',','')
                                    .strip()
                                )
                            else:
                                business.reviews_count = ""
                                
                            if page.locator(reviews_average_xpath).count() > 0:
                                business.reviews_average = float(
                                    page.locator(reviews_average_xpath).get_attribute(name_attibute)
                                    .split()[0]
                                    .replace(',','.')
                                    .strip())
                            else:
                                business.reviews_average = ""
                            
                            
                            business.latitude, business.longitude = self.extract_coordinates_from_url(page.url)
                            self.insert_place(f"{business.name} {business.address}",business.address,CITY_ID,CITY,COUNTRY)
                            # print(business)
                            print(business)
                            business_list.business_list.append(business)
                        except Exception as e:
                            print(f'Error occurred: {e}')
                    
                except:
                        browser.close()
                        pass    
                
    def get_places_data(self,CityID):
        data={
        "filterInfo": [
            {
            "filterTerm":CityID,
            "filterType": "EQUALS",
            "filterBy": "cityId"
            }
            ],
        "pageSize": 100000 
        }
       
        main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS['PLACE_LIST'],json=data,headers=self.headers).json()
        print(main)
        return main['data']
    
    def get_top3_posts_for_place(self,placePk):
      
        urls=[]
        
        posts=self.cl.location_medias_top_v1(placePk,5)
        for data in posts:
            # print(data)
            print(type(data))
            if data["media_type"] == 1:
                urls.append(data["thumbnail_url"])
            elif data["media_type"] == 2 and  data['product_type'] == "clips":
                urls.append(data["thumbnail_url"])
                
            elif data["media_type"] == 8 and  data['product_type'] == "carousel_container":
                urls.append(data['resources'][0]['thumbnail_url'])
        return ",".join(urls)
                
    def update_places(self, places, city ):
        # print(data)
        for plcedetail in places:
            try:
                print(plcedetail)
                place_json=self.get_place_info_from_google(plcedetail['GooglePlaceName'],plcedetail['CityId'],plcedetail["Country"])
                # print(place_json)
                if plcedetail['InstagramLocation']!=None:
                    place_images=self.get_top3_posts_for_place(plcedetail['InstagramLocation'])
                    place_json["MigratedImages"]=place_images
                    if plcedetail['InstagramHandle'] ==None or plcedetail['InstagramHandle']== "":
                        print("kjfnbfdjf;o  in if condition")
                        place_json["InstagramHandle"]=self.extract_insta_url(plcedetail['PlaceName']+" "+ city+" insta")
                    else:
                        place_json["InstagramHandle"]=plcedetail['InstagramHandle']
                    
                    place_json["PlaceId"]=plcedetail['PlaceId']
                    # place_json.pop("ModifiedBy")
                    # place_json.pop("CreatedBy")
                    # place_json.pop("ModifiedDate")
                    # place_json.pop("CreatedDate")
                    # # print(place_json) ###
                    # plcedetail["OpeningHours"]=place_json["OpeningHours"]
                    # plcedetail["Reviews"]=place_json["Reviews"]
                    # plcedetail["Description"]=place_json["Description"]
                    # place_json.pop("MigratedImages")
                    print(place_json)
                    res=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS['PLACE_UPDATE'],json=place_json,headers=self.headers).json()
                    print(res)   
                    # time.sleep(10)  
            except Exception as e :
                print(e)
                pass 
        
        
    def Update_current_popilarity_24_7(self,CITY_ID):
    # data={"cityId":"85ab5e34-3d98-406f-a8c1-77df8ed68c2c"}
        print("i am in ")
        self.get_proxies_urls()
        data={
        "filterInfo": [
            {
            "filterTerm":CITY_ID,
            "filterType": "EQUALS",
            "filterBy": "cityId"
            
            }
            ],
        "pageSize": 100000 
        }
       
        # print(data)
        main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS['PLACE_LIST'],json=data,headers=self.headers).json()
        # googlePlaceName=[]
        # a=0
       
        # print(main)
        # for i in main["data"]:
        #     a+=1
        #     place_name=i["GooglePlaceName"]
        #     googlePlaceName.append(place_name)
        # rows = googlePlaceName
        # # rows=['park bar atlanta']
        # print(len(rows))

        

        def index_get(array, *argv):
            try:
                for index in argv:
                    array = array[index]
                return array
            except (IndexError, TypeError):
                return None
        
        updateRecords = []
        def get_it(place_data):
            try:
                
                USER_AGENT = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/54.0.2840.98 Safari/537.36"}
                params_url = {
                "tbm": "map",
                "tch": 1,
                "hl": "en",
                "q": urllib.parse.quote_plus(place_data["GooglePlaceName"]),
                "pb": "!4m12!1m3!1d4005.9771522653964!2d-122.42072974863942!3d37.8077459796541!2m3!1f0!2f0!3f0!3m2!1i1125!2i976"
                    "!4f13.1!7i20!10b1!12m6!2m3!5m1!6e2!20e3!10b1!16b1!19m3!2m2!1i392!2i106!20m61!2m2!1i203!2i100!3m2!2i4!5b1"
                    "!6m6!1m2!1i86!2i86!1m2!1i408!2i200!7m46!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!"
                    "1m3!1e4!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e"
                    "10!2b0!3e4!2b1!4b1!9b0!22m6!1sa9fVWea_MsX8adX8j8AE%3A1!2zMWk6Mix0OjExODg3LGU6MSxwOmE5ZlZXZWFfTXNYOGFkWDh"
                    "qOEFFOjE!7e81!12e3!17sa9fVWea_MsX8adX8j8AE%3A564!18e15!24m15!2b1!5m4!2b1!3b1!5b1!6b1!10m1!8e3!17b1!24b1!"
                    "25b1!26b1!30m1!2b1!36b1!26m3!2m2!1i80!2i92!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i976!1m6!1m2!1i1075!2i0!2m2!"
                    "1i1125!2i976!1m6!1m2!1i0!2i0!2m2!1i1125!2i20!1m6!1m2!1i0!2i956!2m2!1i1125!2i976!37m1!1e81!42b1!47m0!49m1"
                    "!3b1"
                    }
                
                search_url = "https://www.google.de/search?" + "&".join(k + "=" + str(v) for k, v in params_url.items())
                logging.info("searchterm: " + search_url)
                
                gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                proxy_handler = urllib.request.ProxyHandler({'http': random.choice(self.proxies)})
                req = urllib.request.Request(url=search_url, data=None, headers=USER_AGENT)
                opener = urllib.request.build_opener(proxy_handler)
                resp = opener.open(req)
                data = resp.read().decode('utf-8').split('/*""*/')[0]
                jend = data.rfind("}")
                if jend >= 0:
                    data = data[:jend + 1]
                
                jdata = json.loads(data)["d"]
                jdata = json.loads(jdata[4:])
                info = index_get(jdata, 0, 1, 0, 14)
                current_popularity = index_get(info, 84, 7, 1)
                # f2=open("mum.txt","a") 
                if current_popularity == None:
                    current_popularity = 0
                if 0<current_popularity <=5:
                    current_popularity=5
                print({ 'googlePlaceName': place_data["GooglePlaceName"], 'currentpopularity': current_popularity, "place_id":place_data["PlaceId"]}, time.time())
                # if current_popularity>70:
                    # print(" current_popularity= "+current_popularity+" name= "+url)
                    # f2.write(f"current_popularity ={current_popularity }, name = {url}\n" )
                # f=open("records.txt","a")
                # f.write(f"Update place set currentpopularity = {current_popularity} where googlePlaceName= '{url}' \n")
                updateRecords.append({ 'googlePlaceName': place_data["GooglePlaceName"], 'currentpopularity': current_popularity, "place_id":place_data["PlaceId"]})
                
            except Exception as e:
                print("Unable to get url {} due to {}.".format(place_data["GooglePlaceName"], e.__class__))
            



        start = time.time()
        with PoolExecutor(max_workers=20) as executor:
            for _ in executor.map(get_it, main["data"]):
                pass
        end = time.time()
        print(len(main["data"]))
        print("Took {} seconds to pull websites.".format(end - start))
        start_updating=time.time()
        insertnumber = 100
        for n in range(int(len(updateRecords)/insertnumber)+1):
            start = (n + 1) * insertnumber
            print(len(updateRecords[n * insertnumber :start]))
            # headers = {'Content-Type': 'application/json',
            #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
            #         "Accept-Encoding": "*",
            #         "Connection": "keep-alive", "Accept": "*/*"
            # print(updateRecords[n * insertnumber :start])
            if self.db=="old":
                response = requests.post(f"{self.BASE_URLS['BASE_URL']}/api/v1/Place/UpdateCurrentPopularity",json=updateRecords[n * insertnumber :start], headers=self.headers, timeout=20 *60)
            else:
                response = requests.post(f"{self.BASE_URLS['BASE_URL']}/Place/UpdateCurrentPopularity",json=updateRecords[n * insertnumber :start], headers=self.headers, timeout=20 *60)
            print(response.content)
            end_update_100=time.time()
            print("Took {} seconds to push websites.".format(end_update_100 - start_updating))
            start_updating=time.time()
        print("Data  inserted to  db ")
   
   
    def add_currentPopularity_history(self,data):
      


        data={
            "PlaceId":data["place_id"],
            "CurrentPopularity": data["currentpopularity"]
        }

        base_url="https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/Analytics/PlacePopulationHistory/insert"
       

        res=requests.post(base_url,json=data,headers=self.headers).json()
        print(res)
       
   
   
    def History_current_popilarity_24_7(self,CITY_ID):
    # data={"cityId":"85ab5e34-3d98-406f-a8c1-77df8ed68c2c"}
        print("i am in ")
        self.get_proxies_urls()
        data={
        "filterInfo": [
            {
            "filterTerm":CITY_ID,
            "filterType": "EQUALS",
            "filterBy": "cityId"
            
            }
            ],
        "pageSize": 100000 
        }
       
        # print(data)
        main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS['PLACE_LIST'],json=data,headers=self.headers).json()
        # googlePlaceName=[]
        # a=0
       
        # print(main)
        # for i in main["data"]:
        #     a+=1
        #     place_name=i["GooglePlaceName"]
        #     googlePlaceName.append(place_name)
        # rows = googlePlaceName
        # # rows=['park bar atlanta']
        # print(len(rows))

        

        def index_get(array, *argv):
            try:
                for index in argv:
                    array = array[index]
                return array
            except (IndexError, TypeError):
                return None
        
        updateRecords = []
        def get_it(place_data):
            try:
                
                USER_AGENT = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/54.0.2840.98 Safari/537.36"}
                params_url = {
                "tbm": "map",
                "tch": 1,
                "hl": "en",
                "q": urllib.parse.quote_plus(place_data["GooglePlaceName"]),
                "pb": "!4m12!1m3!1d4005.9771522653964!2d-122.42072974863942!3d37.8077459796541!2m3!1f0!2f0!3f0!3m2!1i1125!2i976"
                    "!4f13.1!7i20!10b1!12m6!2m3!5m1!6e2!20e3!10b1!16b1!19m3!2m2!1i392!2i106!20m61!2m2!1i203!2i100!3m2!2i4!5b1"
                    "!6m6!1m2!1i86!2i86!1m2!1i408!2i200!7m46!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!"
                    "1m3!1e4!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e"
                    "10!2b0!3e4!2b1!4b1!9b0!22m6!1sa9fVWea_MsX8adX8j8AE%3A1!2zMWk6Mix0OjExODg3LGU6MSxwOmE5ZlZXZWFfTXNYOGFkWDh"
                    "qOEFFOjE!7e81!12e3!17sa9fVWea_MsX8adX8j8AE%3A564!18e15!24m15!2b1!5m4!2b1!3b1!5b1!6b1!10m1!8e3!17b1!24b1!"
                    "25b1!26b1!30m1!2b1!36b1!26m3!2m2!1i80!2i92!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i976!1m6!1m2!1i1075!2i0!2m2!"
                    "1i1125!2i976!1m6!1m2!1i0!2i0!2m2!1i1125!2i20!1m6!1m2!1i0!2i956!2m2!1i1125!2i976!37m1!1e81!42b1!47m0!49m1"
                    "!3b1"
                    }
                
                search_url = "https://www.google.de/search?" + "&".join(k + "=" + str(v) for k, v in params_url.items())
                logging.info("searchterm: " + search_url)
                
                gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                proxy_handler = urllib.request.ProxyHandler({'http': random.choice(self.proxies)})
                req = urllib.request.Request(url=search_url, data=None, headers=USER_AGENT)
                opener = urllib.request.build_opener(proxy_handler)
                resp = opener.open(req)
                data = resp.read().decode('utf-8').split('/*""*/')[0]
                jend = data.rfind("}")
                if jend >= 0:
                    data = data[:jend + 1]
                
                jdata = json.loads(data)["d"]
                jdata = json.loads(jdata[4:])
                info = index_get(jdata, 0, 1, 0, 14)
                current_popularity = index_get(info, 84, 7, 1)
                # f2=open("mum.txt","a") 
                if current_popularity == None:
                    current_popularity = 0
                print({ 'googlePlaceName': place_data["GooglePlaceName"], 'currentpopularity': current_popularity, "place_id":place_data["PlaceId"]}, time.time())
                # if current_popularity>70:
                    # print(" current_popularity= "+current_popularity+" name= "+url)
                    # f2.write(f"current_popularity ={current_popularity }, name = {url}\n" )
                # f=open("records.txt","a")
                # f.write(f"Update place set currentpopularity = {current_popularity} where googlePlaceName= '{url}' \n")
                updateRecords.append({ 'googlePlaceName': place_data["GooglePlaceName"], 'currentpopularity': current_popularity, "place_id":place_data["PlaceId"]})
                
            except Exception as e:
                print("Unable to get url {} due to {}.".format(place_data["GooglePlaceName"], e.__class__))
            



        start = time.time()
        with PoolExecutor(max_workers=20) as executor:
            for _ in executor.map(get_it, main["data"]):
                pass
        end = time.time()
        print(len(main["data"]))
        print("Took {} seconds to pull websites.".format(end - start))
        start_updating=time.time()
        insertnumber = 100
        start = time.time()
        with PoolExecutor(max_workers=20) as executor:
            for _ in executor.map(self.add_currentPopularity_history, updateRecords):
                pass
        end = time.time()
        print(len(main["data"]))
        # for n in range(int(len(updateRecords)/insertnumber)+1):
        #     start = (n + 1) * insertnumber
        #     print(len(updateRecords[n * insertnumber :start]))
        #     # headers = {'Content-Type': 'application/json',
        #     #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
        #     #         "Accept-Encoding": "*",
        #     #         "Connection": "keep-alive", "Accept": "*/*"
        #     # print(updateRecords[n * insertnumber :start])
        #     if self.db=="old":
        #         response = requests.post(f"{self.BASE_URLS['BASE_URL']}/api/v1/Place/UpdateCurrentPopularity",json=updateRecords[n * insertnumber :start], headers=self.headers, timeout=20 *60)
        #     else:
        #         response = requests.post(f"{self.BASE_URLS['BASE_URL']}/Place/UpdateCurrentPopularity",json=updateRecords[n * insertnumber :start], headers=self.headers, timeout=20 *60)
        #     print(response.content)
        end_update_100=time.time()
        print("Took {} seconds to push websites.".format(end_update_100 - start_updating))
        #     start_updating=time.time()
        print("Data  inserted to  db ")
   

    
    def extract_insta_url(self,q):

        url = "https://in.search.yahoo.com/search"
        headers = {
            "user-agent": random.choice(user_agent_list),
        }
        params = {
            "p": f"{q} ",  
        }
        print(q)
        response = requests.get(url, headers=headers, params=params, proxies={'http': random.choice(self.proxies)})
        print(response.status_code)
        if response.status_code == 200:
            try:
                print("i am in success status code ")
                soup = BeautifulSoup(response.content, "html.parser")
                instagram_link = soup.find_all('a', href=lambda href: href and "instagram.com" in href)[0].get("href").split("instagram.com")[-1].split("/")[0].replace("%2f","")
                return instagram_link
            except:
                pass
                
        else:
            return None
    def extract_reviews(self,feature_id,proxi_urls,nect_page_token=""):
        url = 'https://www.google.com/async/reviewSort'
        params = {
            'async': f'feature_id:{feature_id},review_source:All%20reviews,sort_by:qualityScore,is_owner:false,filter_text:,associated_topic:,next_page_token:{nect_page_token},_pms:s,_fmt:pc,_basejs:%2Fxjs%2F_%2Fjs%2Fk%3Dxjs.s.en_GB.pIkW1CnNxCw.2018.O%2Fam%3DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAEAACgIQAAAAAACgAAgAAAAAAAAAAABIAAAAAAAAJCAABEICAAAEAAAAAMACAAAILAABAgAEAAAAAAAEAAAAIEAEYL__OAAAAAAAAAAAAAQCABEAAAAAAHABABAE0d4AAQAAAAgAAAAMAAAAQAAAAQAAAAUAAAAAAAAAAAQAAAAAAAAABAAAAAABAPoBAAAAAAAAAAAAAAACAAAAAABogAIAAvgBAAAAAACAAwAAAAABAQAAOAYGIAAAAAAAAAD3AcDjAeGQwgIAAAAAAAAAAAAAAAABSBDMgfQXBCAAAAAAAAAAAAAAAAAAAJAiaOJyA4AC%2Fdg%3D0%2Fbr%3D1%2Frs%3DACT90oG5XBoPUUq3Sl9BTYQzX6svSLEIOQ%3Fcb%3Dconstant,_basecss:%2Fxjs%2F_%2Fss%2Fk%3Dxjs.s.cv79PgLUhzo.L.B1.O%2Fam%3DAJA6BAgBAAAgAACAGABUABAAAAwAAAAAAAAAAAAAAAAAAAAAAEACAAAABAAAACQAACAAAAAgAgIQMwEAAAQvAAhgFwBAAAAA-AAIpKMC0AAAJCAABEACABAEAAgAAsAGAQAACABAAEBtAABAAAAHAAACACgEAAAAMTAAAAYAAAABAAICCBJAAAYBoAEBkOCXabwAyA9AgQAABAAMABIARUA4wTAAQQUABjwAAgAAAAAAAAAAAAAIABACAAADUAAABBAAoAeAAPABAEgCEQAgCABAgEIAEAAAAAQAAAAAIAACAQAAQgQAOAYGIADAAAAAAACQAAAAAMCQAgIAAAAAAAAAAAAAAAAAQAAMAQAUBAAAAAAAAAAAAAAAAAAAAJACaII%2Fbr%3D1%2Frs%3DACT90oEvYdgd-ZyqZOfp3TnlxplNTzaUHg,_basecomb:%2Fxjs%2F_%2Fjs%2Fk%3Dxjs.s.en_GB.pIkW1CnNxCw.2018.O%2Fck%3Dxjs.s.cv79PgLUhzo.L.B1.O%2Fam%3DAJA6BAgBAAAgAACAGABUABAAAAwAAAAAAAAAAAAAAAAAAAAAAEACAAAABAAAACQAACAAAEAgCgIQMwEAAASvAAhgFwBAAAAA-ABIpKMC0AAAJCAABEICABAEAAgAAsAGAQAILABBAkBtAABAAAAHAAACIGgEYL__OTAAAAYAAAABAAYCCBNAAAYBoHEBkPCX-f4AyQ9AgQgABAAMABIARUA4wTAAQQUABjwAAgAAAAQAAAAAAAAIBBACAAADUPoBBBAAoAeAAPABAEgCEQAgCABogEIAEvgBAAQAAACAIwACAQABQwQAOAYGIADAAAAAAAD3AcDjAeGQwgIAAAAAAAAAAAAAAAABSBDMgfQXBCAAAAAAAAAAAAAAAAAAAJAiaOJyA4AC%2Fd%3D1%2Fed%3D1%2Fdg%3D0%2Fbr%3D1%2Fujg%3D1%2Frs%3DACT90oE_5h45QsQ6GwCal56_gJnalp7XeQ%3Fcb%3Dconstant',
        }
        

        user_agent = random.choice(user_agents_for_reviews)
        headers = {'user-agent': user_agent}
        # headers = {
        # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        # }
        response = requests.get(url, headers=headers, params=params,proxies={'http': random.choice(self.proxies)})
        return response.content
       
    def parse_relative_date(self,input_string: str):
        """
        Parses a relative date string like 'a year ago' and returns the exact datetime.
        :param input_string: The relative date string (e.g., 'a year ago').
        :return: A datetime object representing the parsed date.
        """
        if input_string=="":
            return ""
        now = datetime.now()
        input_string = input_string.lower()
        
        # Define common relative time patterns
        time_multipliers = {
            'year': 365,  # Approximate number of days in a year
            'month': 30,  # Approximate number of days in a month
            'week': 7,
            'day': 1,
            'hour': 1 / 24,
            'minute': 1 / (24 * 60),
            'second': 1 / (24 * 60 * 60),
        }

        # Regex pattern to extract relative time value and units
        match = re.match(r'(?:(a|an|one|\d+)\s+)?(year|month|week|day|hour|minute|second)s?\s+ago', input_string)
        if match:
            quantity = match.group(1) or '1'
            unit = match.group(2)
            
            # Convert quantity to number
            if quantity in ['a', 'an', 'one']:
                quantity = 1
            else:
                quantity = int(quantity)
            
            # Calculate the delta in days
            days_delta = time_multipliers[unit] * quantity
            
            # Return the calculated date
            return (now - timedelta(days=days_delta)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            raise ""

 
       
    def insert_reviews_for_place(self,feature_id,no_of_reviews,placeid,cityid):
        nect_page_token=''
        for it in range(int(no_of_reviews/10)+1):
            try:
                print("i am in the while loop")
                time.sleep(2)
                soup=BeautifulSoup(self.extract_reviews(feature_id,self.proxies,nect_page_token),"lxml")
                f=open("index.html","w", encoding="utf-8")
                f.write(soup.prettify())
                all__review_data=soup.find_all("div",class_="WMbnJf vY6njf gws-localreviews__google-review")
                for i in all__review_data:
                        # print("innnn")
                    try:
                        user_name=i.find("div",class_="TSUbDb").text
                        user_profile=i.find("img",class_="lDY1rd")["src"]
                        try:
                            user_review_text=i.find("span",tabindex="-1").text
                        except:
                            user_review_text=""
                        user_given_star=i.find("span",class_="lTi8oc z3HNkc")['aria-label'].split("out")[0].replace("Rated ","")
                        user_revied_posted_ago=i.find("span",class_="dehysf lTi8oc").text
                        # print(user_given_star)
                        # print(user_revied_posted_ago)
                        try:
                            user_response_from_owner=i.find("div",class_="d6SCIc").text
                            user_response_from_owner_ago=i.find("span",class_="pi8uOe").text
                            # print(user_response_from_owner)
                            # print(user_response_from_owner_ago)
                        except:
                            user_response_from_owner=""
                            user_response_from_owner_ago=""
                        # print(user_response_from_owner)
                        try:
                            images=[ item['style'].split("(")[1].split(")")[0] for item in i.find("g-scrolling-carousel").find_all("div",class_="JrO5Xe")]
                            print(images)
                        except:
                            images=[]
                            # f=open(f"rest{it}.html","w",encoding="utf-8")
                            # f.write(soup.prettify())
                            # break
                        print({
                            "user_name":user_name,
                            "user_profile":user_profile,
                            "user_review_text":user_review_text,
                            "user_given_star":user_given_star,
                            "user_revied_posted_ago":user_revied_posted_ago,
                            "user_response_from_owner":user_response_from_owner,
                            "user_response_from_owner_ago":user_response_from_owner_ago,
                            "images":images
                        })
                        
                        data={
                            "PlaceId":placeid,
                            "CityId":cityid,
                            "Username": user_name, 
                            "UserProfileImage": user_profile, 
                            "Text": user_review_text, 
                            "Rating": user_given_star,
                            "ReviewDate":user_revied_posted_ago,  
                            "OwnerResponse": user_response_from_owner, 
                            "OwnerResponseDate": user_response_from_owner_ago, 
                            "Images":",".join(images)
                        }
                        print(data)

                        base_url=f"{self.BASE_URLS["BASE_URL"]}/Review/insert"
                    

                        res=requests.post(base_url,json=data,headers=self.headers).json()
                        print(res)
        
                        
                    except Exception as e:
                        # f=open(f"rest{it}.html","w",encoding="utf-8")
                        # f.write(soup.prettify())
                        print(e)
                        
                nect_page_token=soup.find("div",class_="gws-localreviews__general-reviews-block")['data-next-page-token'].replace("==","")
            except:
                pass    
            
            
    def insert_reviews_for_all_place(self,places):
        for i in places:
            print("    ")
            print("    ")
            print("    ")
            # print(i)
            if i["ReviewsID"] != None:
                self.insert_reviews_for_place(i["ReviewsID"],i["Rating_N"] or i["Rating_n"],i["PlaceId"],i["CityId"])
                print(":doneeee")
               
    def get_cities_by_country(self,country_name):
        with open("cities.json", "r", encoding="utf-8") as file:
            cities_data = json.load(file)
            city_list = [
                {
                    "CityName": city["name"],
                    "Latitude": city["lat"],
                    "Longitude": city["lng"],
                    "Country":country_name,
                    "IsScouter":False
                }
                for city in cities_data if city["country"].lower() == country_name.lower()
            ]
            
            return city_list
   