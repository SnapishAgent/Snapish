import requests
import os

# 환경변수에서 WEATHER_API_KEY를 가져옵니다.
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_BASE_URL = 'http://api.weatherapi.com/v1/current.json'

# 환경변수에서 WEATHER_API_KEY를 가져옵니다.
KHOA_API_KEY = os.getenv('KHOA_API_KEY')
KHOA_API_BASE_URL = 'http://api.weatherapi.com/v1/current.json'

def get_weather_by_coordinates(lat, lon):
    """
    Get Current Weather info by using latitude & longitude
    """
    try:
        # 날씨 API 호출
        weather_url = f"{WEATHER_API_BASE_URL}"
        params = {
            "key": WEATHER_API_KEY,
            "q": f"{lat},{lon}",
            "lang": "ko"
        }
        response = requests.get(weather_url, params=params)
        data = response.json()

        if 'error' in data:
            raise ValueError(data['error']['message'])
        
        # 날씨 데이터 가공
        weather_data = data
        return weather_data

    except Exception as e:
        raise Exception(f"Error fetching weather data: {str(e)}")