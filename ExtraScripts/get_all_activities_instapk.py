import requests
from pymongo import MongoClient
import threading

def fetch_instagram_pks(api_url, headers, filter_data):
    """Fetch InstagramPk values from the API."""
    try:
        response = requests.post(api_url, json=filter_data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return [item["InstagramPk"] for item in response.json().get("data", []) if "InstagramPk" in item]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return []

def add_to_mongodb(insta_pks, mongodb_uri, db_name, collection_name):
    """Add InstagramPk values to MongoDB if not already present."""
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]

    for insta_pk in insta_pks:
        if not collection.find_one({"InstagramPk": insta_pk}):
            collection.insert_one({"InstagramPk": insta_pk})
            print(f"Added InstagramPk: {insta_pk}")
        else:
            print(f"InstagramPk {insta_pk} already exists. Skipping.")

    client.close()

def multithread_addition(insta_pks, mongodb_uri, db_name, collection_name, num_threads=4):
    """Divide the list among threads and process them concurrently."""
    # Divide the list of InstagramPk values into chunks for threads
    chunk_size = len(insta_pks) // num_threads + (len(insta_pks) % num_threads > 0)
    threads = []

    for i in range(num_threads):
        chunk = insta_pks[i * chunk_size:(i + 1) * chunk_size]
        thread = threading.Thread(target=add_to_mongodb, args=(chunk, mongodb_uri, db_name, collection_name))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

# Input data
api_url = "https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/Activity/list"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <your_token>"
}
filter_data = {
    "filterInfo": [
        {
            "filterTerm": "723289d5-9983-4a2f-6538-08dcc857d3e1",
            "filterType": "EQUALS",
            "filterBy": "cityId"
        }
    ],
    "pageSize": 100000 
}
# mongodb_uri = "mongodb://localhost:27017/"  # Replace with your MongoDB URI
# db_name = "scouterDB"  # Replace with your database name
# collection_name = "instagram_pks"  # Replace with your collection name


# Input data
api_url = "https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/Activity/list"
headers ={
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NzNhZWViYS00Y2FlLTRjODktYjhlZS05OWYzNDFiYTM2NmMiLCJVc2VySWQiOiI3NzNhZWViYS00Y2FlLTRjODktYjhlZS05OWYzNDFiYTM2NmMiLCJEZXZpY2VJZCI6IjUzNzM4ODBGLTkwN0UtNDc4NS04MjZELUUyRUZDREVCNzc0RCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjEyLzI4LzIwMjQgMTg6Mzc6MzciLCJuYmYiOjE3MzU0MTEwNTcsImV4cCI6MTc2Njk0NzA1NywiaWF0IjoxNzM1NDExMDU3fQ.1HQWE1HYZy08MTT7YOCuLDTQtz_8ZxM6MzCZpBWhs9I"
    }
filter_data = {
    "filterInfo": [
        {
            "filterTerm": "723289d5-9983-4a2f-6538-08dcc857d3e1",
            "filterType": "EQUALS",
            "filterBy": "cityId"
        }
    ],
    "pageSize": 100000 
}

# Main script
insta_pks = fetch_instagram_pks(api_url, headers, filter_data)
if insta_pks:
    multithread_addition(insta_pks, mongodb_uri, db_name, collection_name, num_threads=4)
else:
    print("No InstagramPk data to process.")
