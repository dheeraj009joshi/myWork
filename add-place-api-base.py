
import requests
from utils import zipcodes,user_agent_list
import io
import json
import logging
import random
import re
import ssl
from urllib.parse import quote
from hikerapi import Client
import urllib.request

mobile_urls={
    
    "BASE_URL":"https://scouterlive.azurewebsites.net",
    "PLACE_INSERT":"/api/v1/Place/Insert",
    "PLACE_UPDATE":"/api/v1/Place/Update",
    "PLACE_DELETS":"/api/v1/Place/Delete",
    "COMMENT_INSERT":"",
    "COMMENT_UPDATE":"",
    "COMMENT_DELETS":""
}


PROXIES_SEARCH_URL1='http://list.didsoft.com/get?email=tikuntechnologies@gmail.com&pass=bwnh68&pid=http1000&showcountry=no'
PROXIES_SEARCH_URL2='http://list.didsoft.com/get?email=tikuntechnologies@gmail.com&pass=bwnh68&pid=http1000&showcountry=no&leve2=1&country=US'
PROXIES_SEARCH_URL3='http://list.didsoft.com/get?email=tikuntechnologies@gmail.com&pass=bwnh68&pid=http1000&showcountry=no&leve3=1&country=US'

class ScouterPlaces:
    
    def __init__(self):
        self.cl=Client("zkixRmPS48UJQYoGMFnFNi1pFS9tH3cx")
        self.proxies=[]
        self.headers= {
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzE0LzIwMjQgMDQ6MDI6NTAiLCJuYmYiOjE3MzE1NTY5NzAsImV4cCI6MTc2MzA5Mjk3MCwiaWF0IjoxNzMxNTU2OTcwfQ.MkSV__2iuV2IOSpissPc3HlSD_YEzlj7CPCJZkHfxvE"
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
        try:
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
                    return ["0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
                            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
                            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
                            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
                            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
                            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
                            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"],['null','null','null','null','null','null','null']

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
            f=io.open("data.txt","w",encoding='utf8')
            f.write(data)
            jend = data.rfind("}")
            if jend >= 0:
                data = data[:jend + 1]

            jdata = json.loads(data)["d"]
            jdata = json.loads(jdata[4:])

            info = index_get(jdata, 0, 1, 0, 14)
            ff=open("index.txt","w",encoding="utf-8")
            ff.write(str(info))
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



            a=open("info_27.txt","w",encoding="utf-8")
            a.write(str(index_get(info)))
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

            print(index_get(info, 34,1))
            OpeningHour= extract_opening_hours(index_get(info, 34,1)) or ""
            print(OpeningHour)
            review_text_= [i[1] for i in index_get(info, 31,1) ]
            review_text = ",".join(review_text_)
            print(review_text)
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
        except:
            print("exception occer")
            return None
            
    def insert_place(self,placename,address,CITY_ID,CITY,COUNTRY):
        self.get_proxies_urls()
        data=self.get_place_info_from_google(placename,CITY_ID,COUNTRY)
        if data!=None:
            if data["PlaceName"]!="":
                print("getting images and all")
                aa=self.cl.fbsearch_places_v1(placename,data['Latitude'],data["Longitude"])[0]["pk"]
                data["InstagramLocation"]=aa
                data["MigratedImages"]=self.get_top3_posts_for_place(aa)
                print(data)
                res=requests.post(mobile_urls['BASE_URL']+mobile_urls['PLACE_INSERT'],json=data,headers=self.headers).json()
                print(res)
                return res
            elif data["PlaceName"]!="":
                data=self.get_place_info_from_google(placename.replace(address,"")+" "+CITY+" "+COUNTRY,CITY_ID,COUNTRY)
                if data["PlaceName"]!="":
                    print("getting images and all")
                    aa=self.cl.fbsearch_places_v1(placename,data['Latitude'],data["Longitude"])[0]["pk"]
                    data["InstagramLocation"]=aa
                    data["MigratedImages"]=self.get_top3_posts_for_place(aa)
                    print(data)
                    res=requests.post(mobile_urls['BASE_URL']+mobile_urls['PLACE_INSERT'],json=data,headers=self.headers).json()
                    print(res)
                    return res
        else :
            return {"status":False,"message":"place can't found by script "}

            

    def get_top3_posts_for_place(self,placePk):
      
        urls=[]
        
        posts=self.cl.location_medias_top_v1(placePk,5)
        for data in posts:
            print(data)
            print(type(data))
            if data["media_type"] == 1:
                urls.append(data["thumbnail_url"])
            elif data["media_type"] == 2 and  data['product_type'] == "clips":
                urls.append(data["thumbnail_url"])
                
            elif data["media_type"] == 8 and  data['product_type'] == "carousel_container":
                urls.append(data['resources'][0]['thumbnail_url'])
        return ",".join(urls)
                

aa=ScouterPlaces()
aa.insert_place(placename="Hyde Park Book Club",address="27-29 Headingley Ln., Headingley, Leeds LS6 1BL, United Kingdom",CITY_ID="723289d5-9983-4a2f-6538-08dcc857d3e1",CITY="Leeds",COUNTRY="UK") # pass the following inputs 

