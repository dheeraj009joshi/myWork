import csv
import json
import random
import requests 
import re
from .config import mobile_urls,PROD_URLS
from hikerapi import Client
url = 'https://scouterlive.azurewebsites.net/api/v1/Videos/Insert'
commenturl = 'https://scouterlive.azurewebsites.net/api/v1/Comment/Insert'
userUrl = 'https://scouterlive.azurewebsites.net/api/v1/Users/InstagramUser'

class GetPosts():
    def __init__(self,DB) :
        if DB=="old":
            self.BASE_URLS=mobile_urls
        else:
            self.BASE_URLS=PROD_URLS
        self.cl=Client("zkixRmPS48UJQYoGMFnFNi1pFS9tH3cx")
        self.headers= {
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzE0LzIwMjQgMDQ6MDI6NTAiLCJuYmYiOjE3MzE1NTY5NzAsImV4cCI6MTc2MzA5Mjk3MCwiaWF0IjoxNzMxNTU2OTcwfQ.MkSV__2iuV2IOSpissPc3HlSD_YEzlj7CPCJZkHfxvE"
    }
        
    def extract_emoji(self,text):
        try:
            for char in str(text):
                if char.isprintable() and char.encode('utf-8').startswith(b'\xf0'):
                    first_emoji = char
                    break

            unicode_value = f"{ord(first_emoji):04X}"
            return unicode_value
        except:
            return ""
                
                

        # Get the Unicode of the first emoji
       
    
    def extract_hashtags(self,text):
        hashtags = re.findall(r"#\w+", text)
        # Create the JSON-like dictionary with formatted keys
        jsn = {f"Hashtag{i+1}": hashtags[i] if i < len(hashtags) else '' for i in range(5)}
        return jsn

    def insertUser(self,userData):
        # to - do need to handle used id
        # biography = re.sub("([#@])\\w+", "", userData["biography"] or "")
        reqjsn = {
            'Name': userData["username"],
            'FullName': str(userData["full_name"]),
            'MigratedProfileImage': userData["profile_pic_url"],
            'InstagramVerified': userData["is_verified"],
            'InstagramPk': userData['pk']
        }
        print({"user data":reqjsn})
        headers = {
            "Content-Type": "application/json",
            }
        res=requests.post(userUrl,json=reqjsn,headers=headers).json()
        print(res)
        return res['result']   
    
    
    def get_place_id(self,data):
        
        place_id=""
        
        filter_data={"filterInfo": [
                {
                "filterTerm":data["PlaceName"],
                "filterType": "EQUALS",
                "filterBy": "PlaceName"
                }
                ]
            }

        main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS["PLACE_LIST"],json=filter_data,headers=self.headers).json()
        print(main)
        
        if main["total"]>0:
            print(" place  found ")
            place_id=main["data"][0]['PlaceId']
            print(place_id)
        else:
            print(" place not found inserting place ")
            main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS["PLACE_INSERT"],json=data,headers=self.headers).json()
            print(main) 
            place_id=main['result']
            

        return place_id
 
    def insert_activity(self,post, HASHTAG, ActivityType,AttachmentType, CityID, PlaceId):
        jsn = {"Hashtag1": '', "Hashtag2": '',
            "Hashtag3": '', "Hashtag4": '', "Hashtag5": ''}
        caption = re.sub("([#@])\\w+", "", post["caption_text"] or "")
        reqjsn = {
        "ActivityType": ActivityType, #["Image", "Video", "Event"]s
        "AttachmentType": AttachmentType, #["Image", "Video"],
        "Title": post['title'],
        "Description": caption.replace("\n", " ").replace("\t", " "),
        "InLocation":  post["location"] != None,
        "TagLocation": None,
        "LikeCount": post['like_count'],
        "AttachmentUrl": post['video_url'],
        "ThumbnailUrl": post["thumbnail_url"],
        "Emoji": "",
        "Hashtag1": HASHTAG,
        "BatchName":"inputs['BatchName']",
        "MigratedUrl": post["thumbnail_url"],
        "MigratedDate": post["taken_at"],
        "Latitude": post["location"] and post["location"]["lat"],
        "Longitude":post["location"] and post["location"]["lng"],
        "PlaceId":PlaceId,
        "CityId":CityID
    }

        print(reqjsn)
        

        res=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS["ACTIVITY_INSERT"],json=reqjsn,headers=self.headers).json()
        print(res)
    
    def postComment(self,post, HASHTAG,  CityID, PlaceId,userId,insta_place_id,BatchName="",images=""):
        jsn = {"Hashtag1": '', "Hashtag2": '',
            "Hashtag3": '', "Hashtag4": '', "Hashtag5": ''}
        caption = re.sub("([#@])\\w+", "", post["caption_text"] or "")
        # datetime_object = post["taken_at"].strftime("%Y-%m-%dT%X")
    
        Emoji=self.extract_emoji(caption)
        if Emoji=="":
            Emoji="1F4F7"
            
        jsn=self.extract_hashtags(caption)   
        # print(scrapeDetail[2])
        reqjsn = {
            'InLocation': post["location"] != None,
            'Text': caption.replace("\n", " ").replace("\t", " "),
            'MigratedImage': ",".join(images) if images!="" else post["thumbnail_url"],
            'Latitude': post["location"] and post["location"]["lat"],
            'Longitude': post["location"] and post["location"]["lng"],
            'BatchName':BatchName,
            'Emoji': Emoji,
            'userId': userId,
            "Hashtag": '#'+str(HASHTAG),
            "Hashtag1": '#'+str(HASHTAG),
            "Hashtag2": jsn["Hashtag2"],
            "Hashtag3": jsn["Hashtag3"],
            "Hashtag4": jsn["Hashtag4"],
            "Hashtag5": jsn["Hashtag5"],
            "MigratedDate": post["taken_at"],
            "TimeStamp": post["taken_at"],
            "Hide": False,
            "CityId": CityID,
            "PlaceId":PlaceId,
            "LikeCount":post['like_count'],
            "InstagramPk":post["pk"],
            "InstagramLocation":f'https://www.instagram.com/explore/locations/{insta_place_id}'

        }
        print(reqjsn)
        print()
   
        
        res = requests.post(commenturl, json=reqjsn)
        print('time', 'message',  'inserted comment :- ' + res.text)
        print()
        print()
 
    def lookpost(self,post, HASHTAG,  CityID, PlaceId,userId,insta_place_id,BatchName=""):
        vidurl = post["video_url"]
       
        caption = re.sub("([#@])\\w+", "", post["caption_text"] or "")
        # datetime_object = post["taken_at"].strftime("%Y-%m-%dT%X")
        Emoji=self.extract_emoji(caption)
        if Emoji=="":
            Emoji="1F4F9"
            
        jsn=self.extract_hashtags(caption) 

        reqjsn = {
            'InLocation': post["location"] != None,
            'VideoDescription': caption.replace("\n", " ").replace("\t", " "),
            'MigratedVideoURL': vidurl,
            'MigratedThumbnailURL': post["thumbnail_url"],
            'Latitude': post["location"] and post["location"]["lat"],
            'Longitude': post["location"] and post["location"]["lng"],
            'BatchName':BatchName,
            'Emoji':Emoji,
            'userId': userId,
            "Hashtag": '#'+str(HASHTAG),
            "Hashtag1": '#'+str(HASHTAG),
            "Hashtag2": jsn["Hashtag2"],
            "Hashtag3": jsn["Hashtag3"],
            "Hashtag4": jsn["Hashtag4"],
            "Hashtag5": jsn["Hashtag5"],
            "MigratedDate": post["taken_at"],
            "TimeStamp": post["taken_at"],
            "Hide": False,
            "CityId":CityID,
            "PlaceId":PlaceId,
            "LikeCount":post['like_count'],
            "InstagramPk":post["pk"],
            "InstagramLocation":f'https://www.instagram.com/explore/locations/{insta_place_id}'

        }
        print()
       
        print(reqjsn)
        print()
        res = requests.post(url, json=reqjsn)
        print('time', 'message',  'inserted video :- ' + res.text)
        print()
       
    
    
    
    
    
    
   
    
    
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
        

        main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS["PLACE_LIST"],json=data,headers=self.headers).json()
        return main['data']
    def update_places_data(self,placeId,scrapeDetail):

        main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS["PLACE_UPDATE"],json=scrapeDetail,headers=self.headers).json()
        print( main)

    def test_location_posts(self,scrapeDetails,CityId,batchName):
        for scrapeDetail in scrapeDetails: 
            # try:
                placeId=self.get_place_id(scrapeDetail)
                placename=str(scrapeDetail["GooglePlaceName"])
                address=str(scrapeDetail["Address"])
                lat=str(scrapeDetail["Latitude"])
                long=str(scrapeDetail["Longitude"])
                
                if scrapeDetail['InstagramLocation']==None:
        
                    aa=self.cl.fbsearch_places_v1(placename,lat,long)[0]
                    print(aa)
                    insta_place_id=aa["pk"]
                    scrapeDetail['InstagramLocation']=insta_place_id
                    
                    self.update_places_data(placeId,scrapeDetail)
                    medias=self.cl.location_medias_recent_v1(aa["pk"],15)
                else:
                    print("location id found ")
                    insta_place_id=scrapeDetail['InstagramLocation']
                    medias=self.cl.location_medias_recent_v1(insta_place_id,15)
                    # medias=cl.location_medias_recent_v1(103257511035949)
                print("done")
                for data in medias:
                    uniqueuserid ="C7AB5D9C-4D89-4C3E-964C-91A190F736AF"
                    # uniqueuserid = self.insertUser(userInfo)
                    # user_id.append(
                    #     {'id': userData["pk"], 'userId': uniqueuserid})
                    if data["media_type"] == 1:
                        self.postComment(data, placename.replace(address,""),CityId,placeId,uniqueuserid,insta_place_id,batchName)
                    elif data["media_type"] == 2 and  data['product_type'] == "clips":
                        print("this is video")
                        self.lookpost(data, placename.replace(address,""),CityId,placeId,uniqueuserid,insta_place_id,batchName)
                    elif data["media_type"] == 8 and  data['product_type'] == "carousel_container":
                        urls=[i['thumbnail_url'] for i in data['resources']]
                        print(urls)
                        self.postComment(data, placename.replace(address,""),CityId,placeId,uniqueuserid,insta_place_id,batchName,urls)
                    
            # except:
            #     pass

# aa=GetPosts()
# # aa.select_ig_accounts() ##Get sessions for all the accounts which are in the accounts.csv
# places=aa.get_places_data(city_id) # Get all the places for atlanta 
# # aa.main_scrapper(places,"85ab5e34-3d98-406f-a8c1-77df8ed68c2c")

# aa.test_location_posts(places["data"],city_id,"Dec 11 2024")














