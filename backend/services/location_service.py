import requests
import os

# 환경변수에서 WEATHER_API_KEY를 가져옵니다.
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

def get_location_by_coordinates(lat, lon):
    try:
        url = f"https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={lon}&y={lat}"
        headers = {
            "Authorization": KAKAO_API_KEY,
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes

        data = response.json()

        if "documents" in data and len(data["documents"]) > 0:
            document = next((doc for doc in data["documents"] if doc.get("region_type") == "H"), None)
            if document:
                location_name = document["address_name"]
                return  location_name
            return None  # Return None if no 'H' type is found
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None