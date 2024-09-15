# from apscheduler.schedulers.blocking import BlockingScheduler
import requests as re
import urllib.request
# import schedule
from urllib.error import URLError
import urllib.parse
import time
import ssl
import logging
import json
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
import random
# from Mail_function import mail_send

from config import BASE_URL, CITY_ID, SEARCH_URL1, SEARCH_URL2, SEARCH_URL3

def job():
    # data={"cityId":"85ab5e34-3d98-406f-a8c1-77df8ed68c2c"}
    data={
    "filterInfo": [
        {
        "filterTerm":CITY_ID,
        "filterType": "EQUALS",
        "filterBy": "cityId"
        }
        ]
    }

    main=re.post(f"{BASE_URL}/api/v1/Place/List",json=data).json()
    
    googlePlaceName=[]
    for i in main["data"]:
        # print(i)
        place_name=i["GooglePlaceName"]
        googlePlaceName.append(place_name)
    rows = googlePlaceName
    # rows=['park bar atlanta']
    print(len(rows))

    search_url = SEARCH_URL1
    search_url2 = SEARCH_URL2
    search_url3 = SEARCH_URL3
    urls=[]
    try:
        resp = urllib.request.urlopen(urllib.request.Request(url=search_url, data=None))
        data = resp.read().decode('utf-8').split('/*""*/')[0]
        for i in data.split("\n"):
            urls.append(i)
    except:

        resp = urllib.request.urlopen(urllib.request.Request(url=search_url2, data=None))
        data = resp.read().decode('utf-8').split('/*""*/')[0]
        for i in data.split("\n"):
            urls.append(i)
    print(len(urls))

    def index_get(array, *argv):
        try:
            for index in argv:
                array = array[index]
            return array
        except (IndexError, TypeError):
            return None
    
    updateRecords = []
    def get_it(url):
        try:
            
            USER_AGENT = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/54.0.2840.98 Safari/537.36"}
            params_url = {
            "tbm": "map",
            "tch": 1,
            "hl": "en",
            "q": urllib.parse.quote_plus(url),
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
            proxy_handler = urllib.request.ProxyHandler({'http': random.choice(urls)})
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
            f2=open("mum.txt","a") 
            if current_popularity == None:
                current_popularity = 0
            print(current_popularity, time.time())
            if current_popularity>70:
                # print(" current_popularity= "+current_popularity+" name= "+url)
                f2.write(f"current_popularity ={current_popularity }, name = {url}\n" )
            f=open("records.txt","a")
            f.write(f"Update place set currentpopularity = {current_popularity} where googlePlaceName= '{url}' \n")
            updateRecords.append({ 'googlePlaceName': url, 'currentpopularity': current_popularity })
            
        except Exception as e:
            print("Unable to get url {} due to {}.".format(url, e.__class__))
        



    start = time.time()
    with PoolExecutor(max_workers=20) as executor:
        for _ in executor.map(get_it, rows):
            pass
    end = time.time()
    print(len(rows))
    print("Took {} seconds to pull websites.".format(end - start))
    start_updating=time.time()
    insertnumber = 100
    for n in range(int(len(updateRecords)/insertnumber)+1):
        start = (n + 1) * insertnumber
        print(len(updateRecords[n * insertnumber :start]))
        headers = {'Content-Type': 'application/json',
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
                   "Accept-Encoding": "*",
                   "Connection": "keep-alive", "Accept": "*/*"}
        response = re.post(f"{BASE_URL}/api/v1/Place/UpdateCurrentPopularity",json=updateRecords[n * insertnumber :start], headers=headers, timeout=20 *60)

        print(response.content)
        end_update_100=time.time()
        print("Took {} seconds to push websites.".format(end_update_100 - start_updating))
        start_updating=time.time()
    print("Data  inserted to  db ")

while True:
    # try:
        
        try:
            job()
    
        except exception as error  :
            print(error)
            pass
    #     sender_email = "datamanagement@tikuntech.com"
    #     receiver_email = ["dlovej009@gmail.com"]
    #     password = "Maidenatlanta123"
    #     # message=""
    #     print("Done")
    #     subject="Tikuntech"
    #     message =f" There is some error found in script ."
    #     # mail_send(subject,sender_email,password,receiver_email,message)  
    #     continue
    
    
        


    