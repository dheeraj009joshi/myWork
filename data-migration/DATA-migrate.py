import json
import requests

from scouter.config import PROD_URLS,mobile_urls

data={
        "filterInfo": [
            {
            "filterTerm":"723289d5-9983-4a2f-6538-08dcc857d3e1",
            "filterType": "EQUALS",
            "filterBy": "cityId"
            }
            ],
        "pageSize": 100000 
        }
headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzE5LzIwMjQgMTI6MTU6MDUiLCJuYmYiOjE3MzIwMTg1MDUsImV4cCI6MTc2MzU1NDUwNSwiaWF0IjoxNzMyMDE4NTA1fQ.C3hycswaAgRvhEFesttElyq2CYI0uvqa9Y1nimar3hk"
    }

main=requests.post(mobile_urls['BASE_URL']+mobile_urls['PLACE_LIST'],json=data,headers=headers).json()
print(main)
for i in main["data"]:
    body=i
    print(body)
    rev=body["Reviews"]
    print(rev.replace('"','\"'))
    body["Reviews"]= str(body["Reviews"]).replace('"','\\"')
    print(str(body["Reviews"]))
    json_output = json.dumps(body)
    print(json_output)
    if body["Rating"]!=None:
        aa=requests.post(PROD_URLS['BASE_URL']+PROD_URLS['PLACE_INSERT'],json=json_output,headers=headers).json()
        print(aa)
        