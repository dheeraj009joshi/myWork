import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from pymongo import MongoClient
import requests 
import re
from .config import mobile_urls,PROD_URLS, ALLOWED_CATEGORIES,scouterActivity_db_name, scouterActivity_collection_name,scouterActivity_mondodb_url
from hikerapi import Client
url = 'https://scouterlive.azurewebsites.net/api/v1/Videos/Insert'
commenturl = 'https://scouterlive.azurewebsites.net/api/v1/Comment/Insert'
userUrl = 'https://scouterlive.azurewebsites.net/api/v1/Users/InstagramUser'

class GetPosts():
    def __init__(self,DB) :
        self.db=DB
        if DB=="old":
            self.BASE_URLS=mobile_urls
        else:
            self.BASE_URLS=PROD_URLS
        self.cl=Client("0daja8wqtv3o16jpszpj582tbyduul3t")
        self.headers= {
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NzNhZWViYS00Y2FlLTRjODktYjhlZS05OWYzNDFiYTM2NmMiLCJVc2VySWQiOiI3NzNhZWViYS00Y2FlLTRjODktYjhlZS05OWYzNDFiYTM2NmMiLCJEZXZpY2VJZCI6IjUzNzM4ODBGLTkwN0UtNDc4NS04MjZELUUyRUZDREVCNzc0RCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjEyLzI4LzIwMjQgMTg6Mzc6MzciLCJuYmYiOjE3MzU0MTEwNTcsImV4cCI6MTc2Njk0NzA1NywiaWF0IjoxNzM1NDExMDU3fQ.1HQWE1HYZy08MTT7YOCuLDTQtz_8ZxM6MzCZpBWhs9I"
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
 

    def insert_activity(self,post, HASHTAG, ActivityType,AttachmentType, CityID, PlaceId, BatchName,Images=""):
        try:
            jsn = {"Hashtag1": '', "Hashtag2": '',
                "Hashtag3": '', "Hashtag4": '', "Hashtag5": ''}
            caption = re.sub("([#@])\\w+", "", post["caption_text"] or "")
            Emoji=self.extract_emoji(caption)
            if Emoji=="":
                Emoji="1F4F7"
                
            reqjsn = {
            "ActivityType": ActivityType, #["Image", "Video", "Event"]s
            "AttachmentType": AttachmentType, #["Image", "Video"],
            "Title": post['title'],
            "Description": caption.replace("\n", " ").replace("\t", " ")+"\n"+f"https://www.instagram.com/p/{post["code"]}",
            "InLocation":  post["location"] != None,
            "TagLocation": None,
            "LikeCount": post['like_count'],
            "Emoji": Emoji,
            "Hashtag1": HASHTAG,
            "BatchName":BatchName,
            "MigratedDate": post["taken_at"],
            "Latitude": post["location"] and post["location"]["lat"],
            "Longitude":post["location"] and post["location"]["lng"],
            "PlaceId":PlaceId,
            "CityId":CityID,
            "InstagramPk":post["pk"],
        }
            if ActivityType=="Video":
                reqjsn["MigratedUrl"]=post['video_url']
                reqjsn["MigratedThumbnailUrl"]=post["thumbnail_url"]
            else:
                reqjsn["MigratedUrl"]= ",".join(Images) if Images!="" else post["thumbnail_url"]
            print(reqjsn)
            

            res=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS["ACTIVITY_INSERT"],json=reqjsn,headers=self.headers).json()
            print(res)
        except:
            self.notify_actions_to_admin(f'''Error :- Post Extraction  with Batch :- {BatchName}  got error while inserting post :- \n{reqjsn} :)''')
    
    
    def insert_offer_posts(self,post,post_type,placeId,BatchName):
        
        print(post)
        reqjsn={
            "PlaceId":placeId,
            "Description":",".join(post["hashtags"]),
            "PostType":post_type,
            "BatchName":BatchName
        }
        if post_type=="Image":
            reqjsn["MigratedUrl"]=post["thumbnail_url"]
        elif post_type=="Video":
            reqjsn["MigratedUrl"]=post["video_url"]
        print(reqjsn)
        res=requests.post("https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life//ActivityManagement/OfferPost/insert",json=reqjsn,headers=self.headers).json()
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
        
    def get_all_non_selected_city_places(self):
    
        data={
       
        "pageSize": 100000 
        }
       
        # print(data)
        main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS['PLACE_LIST'],json=data,headers=self.headers).json()
        print(len(main["data"]))
        main=[i for i in main["data"] if i["CityId"] not in ["723289d5-9983-4a2f-6538-08dcc857d3e1","85ab5e34-3d98-406f-a8c1-77df8ed68c2c","dbf6eabb-b3f0-4966-eaa6-08dd14c982f8","7e8bb7f3-e64b-480d-07d4-08dd1b82607a","7c6e7a1f-1c36-4b86-9573-08dd23e0250e","3db38269-5556-4822-9572-08dd23e0250e","4d88fd55-6098-4f6e-9571-08dd23e0250e","472b013d-3cc0-4592-a940-b1176e514372","def3a79c-58f0-46f2-b6e1-b6fe83d6870f","f9225c27-948f-4422-bff1-14c5eba71b2b","4b0a257a-5fa5-4e1d-bc87-c26aab25ab60","4740255f-b754-4c3e-bcf4-b6ada876bf27","73914691-c663-4d65-8e78-f3c1fd398376"
]]
        return main
    def check_for_post(self,insta_pk):
        """Add InstagramPk values to MongoDB if not already present."""
        client = MongoClient(scouterActivity_mondodb_url)
        db = client[scouterActivity_db_name]
        collection = db[scouterActivity_collection_name]
        if not collection.find_one({"InstagramPk": insta_pk}):
            collection.insert_one({"InstagramPk": insta_pk})
            print(f"Added InstagramPk: {insta_pk}")
            client.close()
            return True
        else:
            print(f"InstagramPk {insta_pk} already exists. Skipping.")
            client.close()
            return False

    
    def update_places_data(self,placeId,scrapeDetail):

        main=requests.post(self.BASE_URLS['BASE_URL']+self.BASE_URLS["PLACE_UPDATE"],json=scrapeDetail,headers=self.headers).json()
        print( main)

    def test_location_posts(self,scrapeDetails,CityId,batchName): 
        
        total_places_not_allowed=1
        total_image_posts_added=0
        total_video_posts_added=0
        for scrapeDetail in scrapeDetails: 
            try:
            
                if scrapeDetail["PlaceType"] in ALLOWED_CATEGORIES:

                    placeId=str(scrapeDetail["PlaceId"])
                    cityId=str(scrapeDetail["CityId"])
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
                        if self.check_for_post(data["pk"]):
                            # uniqueuserid ="C7AB5D9C-4D89-4C3E-964C-91A190F736AF"
                            # uniqueuserid = self.insertUser(userInfo)
                            # user_id.append(
                            #     {'id': userData["pk"], 'userId': uniqueuserid})
                            # if self.db=="old":
                                # print(data)
                            # if data["media_type"] == 1:
                            #     self.postComment(data, placename.replace(address,""),CityId,placeId,uniqueuserid,insta_place_id,batchName)
                            # elif data["media_type"] == 2 and  data['product_type'] == "clips":
                            #     print("this is video")
                            #     self.lookpost(data, placename.replace(address,""),CityId,placeId,uniqueuserid,insta_place_id,batchName)
                            # elif data["media_type"] == 8 and  data['product_type'] == "carousel_container":
                            #     urls=[i['thumbnail_url'] for i in data['resources']]
                            #     print(urls)
                            #     self.postComment(data, placename.replace(address,""),CityId,placeId,uniqueuserid,insta_place_id,batchName,urls)
                        # else:
                            # print(data)
                            if data["media_type"] == 1:
                                self.insert_activity(data, placename.replace(address,""),"Image","Image",cityId,placeId,batchName)
                                total_image_posts_added+=1
                            elif data["media_type"] == 2 and  data['product_type'] == "clips":
                                print("this is video")
                                self.insert_activity(data, placename.replace(address,""),"Video","Video",cityId,placeId,batchName)
                                total_video_posts_added+=1
                            elif data["media_type"] == 8 and  data['product_type'] == "carousel_container":
                                urls=[i['thumbnail_url'] for i in data['resources']]
                                print(urls)
                                self.insert_activity(data, placename.replace(address,""),"Image","Image",cityId,placeId,batchName,urls)
                                total_image_posts_added+=1
                
                else :
                    print("place type not allowed :- ",total_places_not_allowed,scrapeDetail["PlaceType"])
                    total_places_not_allowed+=1
                    
               
            except:
                pass
        self.notify_actions_to_admin(f''' Update :-  Posts Extraction with the batch :- {batchName} and city Id :- {CityId} Successfull \nTotal n0. of posts added to db :- {total_image_posts_added+total_places_not_allowed}.\nTotal n0. of posts added to db :- {total_image_posts_added+total_video_posts_added}.\nTotal Image posts :- {total_image_posts_added}. \nTotal Video posts :- {total_video_posts_added}. \nTotal Allowed places :- {len(scrapeDetails)-total_places_not_allowed}''')



    def get_offer_posts(self,scrapeDetails,CityId,batchName):

        total_places_not_allowed=1
        total_image_posts_added=0
        total_video_posts_added=0
        for scrapeDetail in scrapeDetails: 
            try:
            
                if scrapeDetail["PlaceType"] in ALLOWED_CATEGORIES:

                    placeId=str(scrapeDetail["PlaceId"])
                    medias=self.cl.user_stories_by_username_v1(scrapeDetail["InstagramHandle"])
                    print(medias)
                    print("done")
                    for data in medias:
                        if self.check_for_post(data["pk"]):

                            if data["media_type"] == 1:
                                self.insert_offer_posts(data,"Image",placeId,batchName)
                                total_image_posts_added+=1
                            elif data["media_type"] == 2:
                                print("this is video")
                                self.insert_offer_posts(data,"Video",placeId,batchName)
                                total_video_posts_added+=1
                
                else :
                    print("place type not allowed :- ",total_places_not_allowed,scrapeDetail["PlaceType"])
                    total_places_not_allowed+=1
                    
               
            except:
                pass
        self.notify_actions_to_admin(f''' Update :-  Offer Posts Extraction with the batch :- {batchName} and city Id :- {CityId} Successfull \nTotal n0. of posts added to db :- {total_image_posts_added+total_video_posts_added}.\nTotal Image posts :- {total_image_posts_added}. \nTotal Video posts :- {total_video_posts_added}. \nTotal Allowed places :- {len(scrapeDetails)-total_places_not_allowed}''')








       
    def notify_actions_to_admin(self,message):

        # Static SMTP Server Configuration
        SMTP_SERVER = "smtp.hostinger.com"
        SMTP_PORT = 465  # Use 587 for TLS, 465 for SSL
        EMAIL_ADDRESS = "info@tikuntech.com"
        EMAIL_PASSWORD = "Dheeraj@2006"
        receiver_email=["dlovej009@gmail.com","brown@tikuntech.com","j.b.fitterman@gmail.com"]
        def send_email(to_emails, body):
            try:
                # Email content
                subject = "Notification from Scouter DataSystem"

                # Create email message
                msg = MIMEMultipart()
                msg["From"] = EMAIL_ADDRESS
                msg["To"] = ", ".join(to_emails)
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))

                # Connect to SMTP server and send email
                with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_ADDRESS, to_emails, msg.as_string())

                print("Email sent successfully!")
                return True
            except Exception as e:
                print(f"Failed to send email: {e}")
                return False


        send_email(receiver_email, message)

# aa=GetPosts()
# # aa.select_ig_accounts() ##Get sessions for all the accounts which are in the accounts.csv
# places=aa.get_places_data(city_id) # Get all the places for atlanta 
# # aa.main_scrapper(places,"85ab5e34-3d98-406f-a8c1-77df8ed68c2c")

# aa.test_location_posts(places["data"],city_id,"Dec 11 2024")














