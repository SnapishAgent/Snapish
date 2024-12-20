from sqlalchemy import select, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
import json

def insert_tidal_data():
    # 프로젝트 루트 디렉토리를 기준으로 경로 설정
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend의 절대 경로
    JSON_FILE_PATH = os.path.join(BASE_DIR, "data", "tidal_observations.json")

    # JSON 파일 읽기
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            origin_data = json.load(f)
        data = [x for x in origin_data['result']['data']]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        return

    from main import engine, TidalObservation

    # SQLAlchemy 세션 생성
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 기존 obs_post_id 조회
        existing_obs_post_ids = {
            row.obs_post_id for row in session.query(TidalObservation.obs_post_id).all()
        }

        # 삽입할 데이터 필터링
        new_data = []
        for entry in data:
            try:
                # 데이터 유효성 검증 및 타입 변환
                new_data.append(TidalObservation(
                    obs_post_id=entry['obs_post_id'],
                    data_type=entry['data_type'],
                    obs_post_name=entry['obs_post_name'],
                    obs_lat=float(entry['obs_lat']),
                    obs_lon=float(entry['obs_lon']),
                    obs_object=entry['obs_object'],
                ))
            except (KeyError, ValueError, TypeError) as e:
                print(f"Skipping invalid entry: {entry}, Error: {e}")

        # 중복 데이터 필터링
        new_data = [entry for entry in new_data if entry.obs_post_id not in existing_obs_post_ids]

        if not new_data:
            print("No new tidal observations to insert.")
            return

        # 데이터 삽입
        session.bulk_save_objects(new_data)
        session.commit()
        print(f"Inserted {len(new_data)} new tidal observations.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

            
# 데이터 삽입 함수
def insert_fishing_place_data():
    # 프로젝트 루트 디렉토리를 기준으로 경로 설정
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend 디렉토리의 절대 경로
    JSON_FILE_PATH = os.path.join(BASE_DIR, "data", "fishing_place_v1.json")

    # JSON 파일 읽기
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            origin_data = json.load(f)
        data = origin_data['fishing']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        return

    # 데이터 정제: usage_fee를 문자열로 변환
    for place in data:
        if not isinstance(place.get('usage_fee'), str):
            place['usage_fee'] = str(place['usage_fee'])

    from main import engine, FishingPlace

    # SQLAlchemy 세션 생성
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 기존 fishing_place_id 조회
        existing_fishing_place_ids = {
            row.fishing_place_id for row in session.query(FishingPlace.fishing_place_id).all()
        }

        # 삽입할 데이터 필터링
        new_data = []
        for entry in data:
            try:
                # 데이터 유효성 검증 및 타입 변환
                new_data.append(FishingPlace(
                    fishing_place_id=entry['fishing_place_id'],
                    name=entry['name'],
                    type=entry['type'],
                    address_road=entry['address_road'],
                    address_land=entry['address_land'],
                    latitude=float(entry['latitude']),
                    longitude=float(entry['longitude']),
                    phone_number=entry.get('phone_number'),
                    main_fish_species=entry.get('main_fish_species'),
                    usage_fee=entry.get('usage_fee'),
                    safety_facilities=entry.get('safety_facilities'),
                    convenience_facilities=entry.get('convenience_facilities')
                ))
            except (KeyError, ValueError, TypeError) as e:
                print(f"Skipping invalid entry: {entry}, Error: {e}")

        # 중복 데이터 필터링
        new_data = [entry for entry in new_data if entry.fishing_place_id not in existing_fishing_place_ids]

        if not new_data:
            print("No new fishing places to insert.")
            return

        # 데이터 삽입
        session.bulk_save_objects(new_data)
        session.commit()
        print(f"Inserted {len(new_data)} new fishing places.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()



# 서비스 초기화 함수 (앱 시작 시 데이터 삽입 호출)
def initialize_service():
    insert_tidal_data()
    insert_fishing_place_data()
