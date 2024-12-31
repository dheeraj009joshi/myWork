import requests


data={
    "PlaceId": "eb3c1181-4087-4360-af74-08dd0ecffaa7",
    "CurrentPopularity": "100"
}

base_url="https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/Analytics/PlacePopulationHistory/insert"
headers= {
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NzNhZWViYS00Y2FlLTRjODktYjhlZS05OWYzNDFiYTM2NmMiLCJVc2VySWQiOiI3NzNhZWViYS00Y2FlLTRjODktYjhlZS05OWYzNDFiYTM2NmMiLCJEZXZpY2VJZCI6IjUzNzM4ODBGLTkwN0UtNDc4NS04MjZELUUyRUZDREVCNzc0RCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjEyLzI4LzIwMjQgMTg6Mzc6MzciLCJuYmYiOjE3MzU0MTEwNTcsImV4cCI6MTc2Njk0NzA1NywiaWF0IjoxNzM1NDExMDU3fQ.1HQWE1HYZy08MTT7YOCuLDTQtz_8ZxM6MzCZpBWhs9I"
    }

res=requests.post(base_url,json=data,headers=headers).json()
print(res)