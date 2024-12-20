import requests
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# API 키와 base URL 설정
KHOA_API_KEY = os.getenv('KHOA_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')  # API 키를 환경변수로 관리

def get_sea_weather_by_seapostid(obs_data):
    current_date = datetime.now().strftime('%Y%m%d')

    # 병렬로 처리할 함수
    def fetch_api_data(DATA_TYPE, obs_post_id):
        api_url = f"http://www.khoa.go.kr/api/oceangrid/{DATA_TYPE}/search.do"
        params = {
            'ServiceKey': KHOA_API_KEY,
            'ObsCode': obs_post_id,
            'Date': current_date,
            'ResultType': 'json'
        }
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            try:
                api_data = response.json()
            except ValueError:
                return (DATA_TYPE, {'error': 'Invalid JSON response'})

            if 'result' not in api_data or 'data' not in api_data['result']:
                if 'error' in api_data['result']:
                    return (DATA_TYPE, {'error': api_data['result']['error']})
                else:
                    return (DATA_TYPE, {'error': 'Unexpected API response structure'})

            filtered_api_data = api_data['result']['data']
            return (DATA_TYPE, filtered_api_data)
        except requests.exceptions.RequestException as e:
            return (DATA_TYPE, {'error': str(e)})

    # ThreadPoolExecutor를 사용해 병렬 요청 실행
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(fetch_api_data, "tideObsRecent", obs_data['obsrecent']),
            executor.submit(fetch_api_data, "tideObsPreTab", obs_data['obspretab'])
        ]

        results = {
            'obsrecent': {},
            'obspretab': {}
        }
        
        for future in as_completed(futures):
            DATA_TYPE, result = future.result()
            if DATA_TYPE == "tideObsRecent":
                results['obsrecent'] = result
            else:
                results['obspretab'] = result

    return results
    

def get_weather_by_coordinates(lat, lon):
    """
    Get Current Weather info by using latitude & longitude
    """
    try:
        # OpenWeather API 파라미터 설정
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "lang": "kr",
            "units": "metric"
        }
        
        
        OPENWEATHER_API_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
        
        response = requests.get(OPENWEATHER_API_BASE_URL, params=params)
        data = response.json()
        
        if response.status_code != 200:
            raise ValueError(data.get('message', 'Unknown error occurred'))
        
        try:
            return process_weather_data(data)
        except Exception as e:
            raise Exception(f"Error Preprocessing weather data: {str(e)}")

    except Exception as e:
        raise Exception(f"Error fetching weather data: {str(e)}")
    
    
def get_wind_direction(degrees):
    """Convert wind degrees to cardinal direction"""
    directions = [
        "북", "북북동", "북동", "동북동", "동", "동남동", "남동", "남남동",
        "남", "남남서", "남서", "서남서", "서", "서북서", "북서", "북북서"
    ]
    index = round(degrees / (360 / len(directions))) % len(directions)
    return directions[index]

def process_weather_data(data):
    return {
        "weather" :{
            "temp": data['main']['temp'],
            "temp_min": data['main']['temp_min'],
            "temp_max": data['main']['temp_max'],
            "humidity": data['main']['humidity'],
            "pressure": data['main']['pressure'],
            "wind_speed": data['wind']['speed'],
            "wind_deg": get_wind_direction(data['wind']['deg']),
            "weather": data['weather'][0]['description'],
            "sunrise": datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'),
            "sunset": datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S')
            }
    }