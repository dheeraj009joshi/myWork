from flask import Flask, render_template, request, jsonify
import threading
import time
import uuid
import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scouter.PlaceClass import ScouterPlaces

app = Flask(__name__)

# Store active threads and their information
active_threads = {
    'cities': {},
    'places': {}
}
thread_store = {
    'cities': {},
    'places': {}
}

def get_cities():
        filter_data={"filterInfo": [
                {
                "filterTerm":True,
                "filterType": "EQUALS",
                "filterBy": "IsScouter"
                }
                ]
            }
        headers=headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1ZXIiOiJub0ZldmVyIiwidW5pcXVlX25hbWUiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJVc2VySWQiOiI3NDQzN2U1Ny1jOGEwLTQxYTAtYTZmMi1iNjQwYzlhNGIyMzciLCJEZXZpY2VJZCI6IjFCREVEODlCLUI1OTAtNEYwQy1BRTc0LUMyODY0OTRFMDNEOCIsIk9yZ2FuaXphdGlvbklkIjoiMmY4MTE1NzctNTZlYy00YmRmLThlM2MtNjE5MGZkYzYzYmE4IiwiVGltZSI6IjExLzE5LzIwMjQgMTI6MTU6MDUiLCJuYmYiOjE3MzIwMTg1MDUsImV4cCI6MTc2MzU1NDUwNSwiaWF0IjoxNzMyMDE4NTA1fQ.C3hycswaAgRvhEFesttElyq2CYI0uvqa9Y1nimar3hk"
        }
        
        main=requests.post(f"https://portal.maiden-ai.com/api/v1/cube/Scouter Galactic Pvt Ltd/night life/scoutermap/City/list",json=filter_data,headers=headers).json()
        print(main)
        cities=[]
        if main["total"]>0:
            for i in main["data"]:
                city_id=i['CityId']
                city_name=i['CityName']
                cities.append({"id": city_id, "name": city_name})
        return cities

def process_city(city_id, city_name, country, thread_id):
    try:
        thread_store['cities'][thread_id]['status'] = 'running'
        thread_store['cities'][thread_id]['message'] = f"Starting ScouterPlaces for {city_name}, {country}"
        
        # Initialize and run ScouterPlaces
        scouter = ScouterPlaces("new")
        scouter.get_proxies_urls()
        scouter.insert_all_places_for_city(city_id, city_name, country)
        
        thread_store['cities'][thread_id]['status'] = 'completed'
        thread_store['cities'][thread_id]['message'] = f"Completed processing {city_name}, {country}"
    except Exception as e:
        thread_store['cities'][thread_id]['status'] = 'error'
        thread_store['cities'][thread_id]['message'] = f"Error processing {city_name}: {str(e)}"
    finally:
        if thread_id in active_threads['cities']:
            del active_threads['cities'][thread_id]

def process_place(city_id, place_name, address, thread_id):
    try:
        thread_store['places'][thread_id]['status'] = 'running'
        thread_store['places'][thread_id]['message'] = f"Starting processing for {place_name} at {address}"
        
        # Initialize and run ScouterPlaces
        scouter = ScouterPlaces("new")

        city_data = scouter.get_city_data(city_id)
        scouter.get_proxies_urls()
        scouter.insert_place(place_name,address,city_id,city_data["CityName"], city_data["Country"],is_manual=True)  # Assuming UK as default
        
        thread_store['places'][thread_id]['status'] = 'completed'
        thread_store['places'][thread_id]['message'] = f"Completed processing {place_name} at {address}"
    except Exception as e:
        thread_store['places'][thread_id]['status'] = 'error'
        thread_store['places'][thread_id]['message'] = f"Error processing {place_name}: {str(e)}"
    finally:
        if thread_id in active_threads['places']:
            del active_threads['places'][thread_id]

@app.route('/')
def index():
    return render_template('index.html',cities=get_cities())

@app.route('/start_city_thread', methods=['POST'])
def start_city_thread():
    city_id = request.form.get('city_id')
    city_name = request.form.get('city_name')
    country = request.form.get('country', 'UK')
    
    if not city_id or not city_name:
        return jsonify({'error': 'City ID and City Name are required'}), 400
    
    thread_id = str(uuid.uuid4())
    
    thread_store['cities'][thread_id] = {
        'city_id': city_id,
        'city_name': city_name,
        'country': country,
        'status': 'starting',
        'start_time': time.strftime("%Y-%m-%d %H:%M:%S"),
        'message': 'Initializing process...'
    }
    
    thread = threading.Thread(
        target=process_city,
        args=(city_id, city_name, country, thread_id),
        daemon=True
    )
    thread.start()
    
    active_threads['cities'][thread_id] = thread
    
    return jsonify({
        'success': True,
        'thread_id': thread_id,
        'message': f'Started processing {city_name}, {country}'
    })

@app.route('/start_place_thread', methods=['POST'])
def start_place_thread():
    city_id = request.form.get('city_id')
    place_name = request.form.get('place_name')
    address = request.form.get('address')
    
    if not city_id or not place_name or not address:
        return jsonify({'error': 'All fields are required'}), 400
    
    thread_id = str(uuid.uuid4())
    
    thread_store['places'][thread_id] = {
        'city_id': city_id,
        'place_name': place_name,
        'address': address,
        'status': 'starting',
        'start_time': time.strftime("%Y-%m-%d %H:%M:%S"),
        'message': 'Initializing process...'
    }
    
    thread = threading.Thread(
        target=process_place,
        args=(city_id, place_name, address, thread_id),
        daemon=True
    )
    thread.start()
    
    active_threads['places'][thread_id] = thread
    
    return jsonify({
        'success': True,
        'thread_id': thread_id,
        'message': f'Started processing {place_name} at {address}'
    })

@app.route('/get_threads/<type>')
def get_threads(type):
    processing_count = sum(1 for t in thread_store[type].values() if t['status'] in ['running', 'starting'])
    
    return jsonify({
        'threads': thread_store[type],
        'active_count': processing_count
    })

@app.route('/stop_thread/<type>/<thread_id>', methods=['POST'])
def stop_thread(type, thread_id):
    if thread_id in active_threads[type]:
        thread = active_threads[type][thread_id]
        
        if thread.is_alive():
            thread_store[type][thread_id]['status'] = 'stopped'
            thread_store[type][thread_id]['message'] = 'Processing stopped by user'
            del active_threads[type][thread_id]
            return jsonify({'success': True, 'message': 'Thread stopped successfully'})
        else:
            del active_threads[type][thread_id]
            return jsonify({'success': False, 'message': 'Thread was not running'})
    else:
        return jsonify({'success': False, 'error': 'Thread not found'}), 404

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=51000)
    # app.run(debug=True,port=5000)

