# from hikerapi import Client

# scouter=Client("0daja8wqtv3o16jpszpj582tbyduul3t")
# aa=scouter.fbsearch_places_v1("PRYZM",53.801122100,-1.544679700)[0]
# print(aa)
# import requests
# url = "https://api.hikerapi.com/v2/user/explore/businesses/by/id?user_id=167340899"
# headers = {
#     "accept": "application/json",
#     "x-access-key": "0daja8wqtv3o16jpszpj582tbyduul3t"
# }
# response = requests.get(url, headers=headers)
# if response.status_code == 200:
#     print(response.json())
# else:
#     print(f"Error: {response.status_code}")
#     print(response.text)


from geopy.geocoders import Nominatim

# Create a geolocator object
geolocator = Nominatim(user_agent="my_geopy_app")

# Address or place name
address = "Freehand Miami"

# Perform geocoding
location = geolocator.geocode(address)

if location:
    print(f"Address: {location.address}")
    print(f"Latitude: {location.latitude}")
    print(f"Longitude: {location.longitude}")
    # Extract city name from `display_name` or fallback fields
    address_details = location.address.split(",")[-1]
    print(address_details)
    