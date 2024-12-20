import os
import logging
from datetime import datetime, timedelta
import uuid
from werkzeug.utils import secure_filename
import base64

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
from functools import wraps
import jwt
import torch
import io
import requests

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    ForeignKey,
    Enum,
    Boolean,
    Text,
    DECIMAL,
    JSON,
    Float,
    VARCHAR,
    text
)
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from services.weather_service import get_sea_weather_by_seapostid, get_weather_by_coordinates
from services.lunar_mulddae import get_mulddae_cycle, calculate_moon_phase
from services.initialize_db import initialize_service
from ultralytics import YOLO
from flask_cors import CORS

# Ensure the 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    Check if the file has one of the allowed extensions.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 환경 변수 로드
load_dotenv("./.env")

SQL_KEY = os.getenv("SQL_KEY")

# 데이터베이스 설정
DATABASE_URL = os.getenv('DATABASE_URL', f'mysql+pymysql://root:{SQL_KEY}@localhost:3306/snapish')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = scoped_session(sessionmaker(bind=engine))

# 베이스 모델 선언
Base = declarative_base()

# 데이터베이스 모델 정의
class User(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    full_name = Column(String(100))
    age = Column(Integer)
    preferred_font_size = Column(Enum('small', 'medium', 'large'), default='medium')
    avatar = Column(String(255), nullable=True)  # New field for avatar
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship('UserSession', back_populates='user', cascade='all, delete')
    locations = relationship('Location', back_populates='user', cascade='all, delete')
    catches = relationship('Catch', back_populates='user', cascade='all, delete')
    rankings = relationship('Ranking', back_populates='user', cascade='all, delete')
    ai_consent = relationship('AIConsent', back_populates='user', uselist=False, cascade='all, delete')
    fish_diaries = relationship('FishDiary', back_populates='user', cascade='all, delete')
    posts = relationship('CommunicationBoard', back_populates='user', cascade='all, delete')
    tournament_participants = relationship('TournamentParticipant', back_populates='user', cascade='all, delete')


class UserSession(Base):
    __tablename__ = 'UserSessions'

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    session_token = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship('User', back_populates='sessions')


class Location(Base):
    __tablename__ = 'Locations'

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    address = Column(String(255))
    manual_entry = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='locations')
    weather_data = relationship('WeatherData', back_populates='location', cascade='all, delete')
    catches = relationship('Catch', back_populates='location', cascade='all, delete')


class FishSpecies(Base):
    __tablename__ = 'FishSpecies'

    species_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum('freshwater', 'saltwater'), nullable=False)
    is_prohibited = Column(Boolean, default=False)
    prohibited_season_start = Column(DateTime)
    prohibited_season_end = Column(DateTime)
    seasonal_info = Column(String(255))
    bait_recommendation = Column(String(255))

    catches = relationship('Catch', back_populates='species')


class Catch(Base):
    __tablename__ = 'Catches'

    catch_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    location_id = Column(Integer, ForeignKey('Locations.location_id', ondelete='CASCADE'))
    species_id = Column(Integer, ForeignKey('FishSpecies.species_id', ondelete='SET NULL'))
    catch_date = Column(DateTime, default=datetime.utcnow)
    fish_size_cm = Column(DECIMAL(5, 2))
    photo_url = Column(String(255))
    exif_data = Column(JSON)

    user = relationship('User', back_populates='catches')
    location = relationship('Location', back_populates='catches')  # Existing line
    species = relationship('FishSpecies', back_populates='catches')  # Existing line
    tournament_participants = relationship('TournamentParticipant', back_populates='catch')  # Add this line
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIConsent(Base):
    __tablename__ = 'AIConsent'

    consent_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'), unique=True)
    consent_given = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='ai_consent')


class FishDiary(Base):
    __tablename__ = 'FishDiaries'

    diary_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    title = Column(String(255))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='fish_diaries')


class CommunicationBoard(Base):
    __tablename__ = 'CommunicationBoard'

    post_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    title = Column(String(255))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='posts')


class WeatherData(Base):
    __tablename__ = 'WeatherData'

    weather_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey('Locations.location_id', ondelete='CASCADE'))
    date = Column(DateTime, default=datetime.utcnow)
    weather_info = Column(JSON)
    tide_data = Column(JSON)

    location = relationship('Location', back_populates='weather_data')


class Tournament(Base):
    __tablename__ = 'Tournaments'

    tournament_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    participants = relationship('TournamentParticipant', back_populates='tournament', cascade='all, delete')


class TournamentParticipant(Base):
    __tablename__ = 'TournamentParticipants'

    participant_id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('Tournaments.tournament_id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    catch_id = Column(Integer, ForeignKey('Catches.catch_id', ondelete='SET NULL'))
    score = Column(Integer)

    tournament = relationship('Tournament', back_populates='participants')
    user = relationship('User', back_populates='tournament_participants')
    catch = relationship('Catch', back_populates='tournament_participants')

# Add the Ranking class
class Ranking(Base):
    __tablename__ = 'Rankings'

    ranking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='rankings')

# Add the TidalObservation class
class TidalObservation(Base):
    __tablename__ = 'TidalObservations'

    obs_station_id = Column(Integer, primary_key=True, autoincrement=True)
    obs_post_id = Column(String(20), unique=True)  # 고유 키로 설정
    obs_post_name = Column(String(50), nullable=False)
    obs_lat = Column(Float, nullable=False)
    obs_lon = Column(Float, nullable=False)
    data_type = Column(String(50), nullable=False)
    obs_object = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# 낚시터 db 컬럼
class FishingPlace(Base):
    __tablename__ = 'FishingPlace'

    fishing_place_id = Column(Integer, primary_key=True, autoincrement=True)  # 고유 식별자
    name = Column(String(255), nullable=False)  # 낚시터명
    type = Column(String(100), nullable=False)  # 낚시터 유형
    address_road = Column(String(255), nullable=True)  # 소재지 도로명 주소
    address_land = Column(String(255), nullable=True)  # 소재지 지번 주소
    latitude = Column(Float, nullable=False)  # WGS84 위도
    longitude = Column(Float, nullable=False)  # WGS84 경도
    phone_number = Column(String(50), nullable=True)  # 낚시터 전화번호
    main_fish_species = Column(Text, nullable=True)  # 주요 어종
    usage_fee = Column(VARCHAR(500), nullable=True)  # 이 요금
    safety_facilities = Column(Text, nullable=True)  # 안전 시설 현황
    convenience_facilities = Column(Text, nullable=True)  # 편익 시설 현황

# 데이터베이스 테이블 생성
Base.metadata.create_all(engine)

# Flask 앱 초기화
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = YOLO('./models/yolo11m_with_augmentations3_conf85.pt').to(device)

# 초기 DB install
initialize_service()

# 라벨 매핑 (영어 -> 한국어)
labels_korean = {
 0: '감성돔',
 1: '대구',
 2: '꽃게',
 3: '갈치',
 4: '말쥐치',
 5: '넙치',
 6: '조피볼락',
 7: '삼치',
 8: '문치가자미',
 9: '참문어',
 10: '돌돔',
 11: '참돔',
 12: '낙지',
 13: '대게',
 14: '살오징어',
 15: '옥돔',
 16: '주꾸미'
}

# Add this dictionary at the top of your file
PROHIBITED_DATES = {
    "넙치": "",
    "조피볼락": "",
    "참돔": "",
    "감성돔": "05.01~05.31",
    "돌돔": "",
    "명태": "01.01~12.31",
    "대구": "01.16~02.15",
    "살오징어": "04.01~05.31",
    "고등어": "04.01~06.30",
    "삼치": "05.01~05.31",
    "참문어": "05.16~06.30",
    "전어": "05.01~07.15",
    "말쥐치": "05.01~07.31",
    "주꾸미": "05.11~08.31",
    "낙지": "06.01~06.30",
    "참홍어": "06.01~07.15",
    "꽃게": "06.21~08.20",
    "대게": "06.01~11.30",
    "갈치": "07.01~07.31",
    "참조기": "07.01~07.31",
    "붉은대게": "07.10~08.25",
    "옥돔": "07.21~08.20",
    "연어": "10.01~11.30",
    "쥐노래미": "11.01~12.31",
    "문치가자미": "12.01~01.31"
}

# REST API
@app.route('/')
def hello():
    return 'Welcome to SNAPISH'

# 물때 정보 받아오기
@app.route('/backend/mulddae', methods=['POST'])
def get_mulddae():
    now_date = request.form.get('nowdate')
    if not now_date:
        return jsonify({"error": "The 'nowdate' parameter is required"}), 400

    try:
        parsed_date = datetime.strptime(now_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        lunar_date, seohae, other = get_mulddae_cycle(parsed_date)
        moon_phase = calculate_moon_phase(parsed_date)
        json_result = {
            "lunar_date": lunar_date,
            "seohae": seohae,
            "other": other,
            "moon_phase": moon_phase,
        }
        return jsonify(json_result)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  # 실제 서비스에서는 안전한 키로 변경하세요.

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # 헤더에서 토큰 가져오기
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({'message': '토큰이 필요합니다.'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '토큰이 만료되었습니다.'}), 401
        except Exception:
            return jsonify({'message': '토큰 인증에 실패하였습니다.'}), 401

        # Pass user_id to the route
        return f(user_id, *args, **kwargs)
    return decorated

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': '모든 필드를 채워주세요.'}), 400

    session = Session()
    existing_user = session.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        session.close()
        return jsonify({'message': '이미 사용 중인 아이디나 이메일입니다.'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        created_at=datetime.utcnow()
    )

    session.add(new_user)
    session.commit()
    session.close()

    return jsonify({'message': '원가입이 성공적으로 완료되었습니다.'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required.'}), 400

    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # 토큰 생성
            payload = {
                'user_id': user.user_id,
                'exp': datetime.utcnow() + timedelta(hours=24)  # 수정된 부분
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            return jsonify({
                'message': '로그인 성공',
                'token': token,
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    # 필요한 사용자 정보 추가
                }
            })
        else:
            return jsonify({'message': '로그인 실패'}), 401
    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({'message': 'Internal server error'}), 500
    finally:
        session.close()

@app.route('/backend/predict', methods=['POST'])
def predict():
    # Get the image either from 'image' file or 'image_base64' in JSON
    if 'image' in request.files:
        file = request.files['image']
        if not allowed_file(file.filename):
            return jsonify({'error': '유효한 이미지 파일을 업로드해주세요.'}), 400
        img = Image.open(file.stream).convert('RGB')
    else:
        data = request.get_json()
        image_base64 = data.get('image_base64')
        if not image_base64:
            return jsonify({'error': '유효한 이미지 데이터를 업로드해주세요.'}), 400
        image_data = base64.b64decode(image_base64)
        img = Image.open(io.BytesIO(image_data)).convert('RGB')

    try:
        results = model(img, exist_ok=True, device=device)
        detections = []
        
        for result in results:  # Iterate over results
            for cls, conf, bbox in zip(result.boxes.cls, result.boxes.conf, result.boxes.xyxy):
                detections.append({
                    'label': labels_korean.get(int(cls), '알 수 없는 라벨'),
                    'confidence': float(conf),
                    'prohibited_dates': PROHIBITED_DATES.get(labels_korean.get(int(cls), ''), ''),
                    'bbox': bbox.tolist()  # Ensure bbox is included
                })

        detections.sort(key=lambda x: x['confidence'], reverse=True)
        if not detections:
            detections.append({
                'label': '알 수 없음',
                'confidence': 0.0
            })

        session = Session()
        token = request.headers.get('Authorization')
        if token:
            token = token.split(' ')[1]
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                user_id = data['user_id']
                current_user = session.query(User).filter_by(user_id=user_id).first()
            except:
                current_user = None
        else:
            current_user = None

        if current_user:
            # Save detections and image info to the database
            filename = secure_filename(f"{uuid.uuid4().hex}.jpg")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            img.save(file_path, format='JPEG')

            new_catch = Catch(
                user_id=current_user.user_id,
                photo_url=filename,
                exif_data=detections,
                catch_date=datetime.utcnow()
            )
            session.add(new_catch)
            session.commit()
            response_data = {
                'id': new_catch.catch_id,
                'detections': detections,
                'imageUrl': filename
            }
        else:
            # Do not save the image to disk or database
            buffered = io.BytesIO()
            img.save(buffered, format='JPEG')
            img_str = base64.b64encode(buffered.getvalue()).decode()
            response_data = {
                'detections': detections,
                'image_base64': img_str
            }

        session.close()
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({'error': '이미지 처리 중 오류가 발생했습니다.'}), 500

@app.route('/profile', methods=['GET', 'PUT'])
@token_required
def profile(user_id):
    session = Session()
    current_user = session.query(User).filter_by(user_id=user_id).first()
    if not current_user:
        session.close()
        return jsonify({'message': 'User not found'}), 404

    if request.method == 'GET':
        user_data = {
            'user_id': current_user.user_id,
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'age': current_user.age,
            'avatar': current_user.avatar,  # Include avatar URL
            # 필요한 정보 추가
        }
        session.close()
        return jsonify(user_data)
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            session.close()
            return jsonify({'message': 'Invalid input'}), 400
        # 사용자 정보 업데이트
        current_user.username = data.get('username', current_user.username)
        current_user.email = data.get('email', current_user.email)
        current_user.full_name = data.get('full_name', current_user.full_name)
        current_user.age = data.get('age', current_user.age)
        # 비밀번호 변경 처리
        if data.get('current_password') and data.get('new_password'):
            if check_password_hash(current_user.password_hash, data['current_password']):
                current_user.password_hash = generate_password_hash(data['new_password'])
            else:
                session.close()
                return jsonify({'message': '현재 비밀번호가 일치하지 않습니다.'}), 400
        session.add(current_user)
        session.commit()
        session.close()
        return jsonify({'message': '프로필이 성공적으로 업데이트되었습니다.'}), 200

@app.route('/recent-activities', methods=['GET'])
@token_required
def recent_activities(user_id):
    session = Session()
    current_user = session.query(User).filter_by(user_id=user_id).first()
    if not current_user:
        session.close()
        return jsonify({'message': 'User not found'}), 404

    # 최근 활동을 조회하는 로직 (예: 데이터베이스에서 최근 5개의 캐치를 가져오기)
    activities = session.query(Catch).filter_by(user_id=current_user.user_id).order_by(Catch.catch_date.desc()).limit(5).all()
    session.close()
    
    recent_activities = [
        {
            'fish': catch.species.name if catch.species else '알 수 없음',
            'location': catch.location.address if catch.location else '알 수 없음',
            'date': catch.catch_date.strftime('%Y-%m-%d'),
            'image': catch.photo_url or '/placeholder.svg?height=80&width=80',
        }
        for catch in activities
    ]
    
    return jsonify({'activities': recent_activities})

@app.route('/catches', methods=['POST'])
@token_required
def add_catch(user_id):
    data = request.get_json()
    imageUrl = data.get('imageUrl')
    detections = data.get('detections')

    if not imageUrl or not detections:
        return jsonify({'message': '이미지 URL 또는 감지 결과가 필요합니다.'}), 400

    session = Session()
    current_user = session.query(User).filter_by(user_id=user_id).first()
    if not current_user:
        session.close()
        return jsonify({'message': 'User not found'}), 404

    new_catch = Catch(
        user_id=current_user.user_id,
        photo_url=imageUrl,
        exif_data=detections,
        catch_date=datetime.utcnow()
    )
    session.add(new_catch)
    session.commit()
    session.close()

    return jsonify({'message': '캐치가 성공적으로 추가되었습니다.'}), 201

@app.route('/catches', methods=['GET'])
@token_required
def get_catches(user_id):
    session = Session()
    current_user = session.query(User).filter_by(user_id=user_id).first()
    if not current_user:
        session.close()
        return jsonify({'message': 'User not found'}), 404

    catches = session.query(Catch).filter_by(user_id=current_user.user_id).all()
    session.close()

    return jsonify([{
        'id': catch.catch_id,  # Added 'id' field
        'imageUrl': catch.photo_url,
        'detections': catch.exif_data,
        'catch_date': catch.catch_date.strftime('%Y-%m-%d')
    } for catch in catches])

@app.route('/catches/<int:catch_id>', methods=['PUT'])
@token_required
def update_catch(user_id, catch_id):
    data = request.get_json()
    if not data:
        logging.error("Invalid input: No data provided")
        return jsonify({"error": "Invalid input"}), 400

    session = Session()
    current_user = session.query(User).filter_by(user_id=user_id).first()
    if not current_user:
        session.close()
        return jsonify({'message': 'User not found'}), 404

    catch = session.query(Catch).filter_by(catch_id=catch_id, user_id=current_user.user_id).first()
    if not catch:
        logging.error(f"Catch not found: catch_id={catch_id}, user_id={current_user.user_id}")
        session.close()
        return jsonify({"error": "Catch not found"}), 404

    try:
        logging.info(f"Updating catch: {catch_id} for user: {current_user.user_id}")
        catch.photo_url = data.get('imageUrl', catch.photo_url)
        catch.exif_data = data.get('detections', catch.exif_data)
        if 'catch_date' in data:
            catch.catch_date = datetime.strptime(data['catch_date'], '%Y-%m-%d')
        session.commit()
        updated_catch = {
            'id': catch.catch_id,
            'imageUrl': catch.photo_url,
            'detections': catch.exif_data,
            'catch_date': catch.catch_date.strftime('%Y-%m-%d')
        }
        logging.info(f"Catch updated successfully: {updated_catch}")
        session.close()
        return jsonify(updated_catch), 200
    except Exception as e:
        logging.error(f"Error updating catch: {e}")
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500

@app.route('/catches/<int:catch_id>', methods=['DELETE'])
@token_required
def delete_catch(user_id, catch_id):
    session = Session()
    current_user = session.query(User).filter_by(user_id=user_id).first()
    if not current_user:
        session.close()
        return jsonify({'message': 'User not found'}), 404

    catch = session.query(Catch).filter_by(catch_id=catch_id, user_id=current_user.user_id).first()
    if not catch:
        session.close()
        return jsonify({'message': 'Catch not found'}), 404

    try:
        session.delete(catch)
        session.commit()
        session.close()
        return jsonify({'message': 'Catch deleted successfully'}), 200
    except Exception as e:
        session.rollback()
        session.close()
        logging.error(f"Error deleting catch: {e}")
        return jsonify({'error': 'Error deleting catch'}), 500

@app.route('/uploads/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/backend/get-detections', methods=['GET'])
@token_required
def get_detections(user_id):
    imageUrl = request.args.get('imageUrl')
    if not imageUrl:
        return jsonify({'error': 'imageUrl is required'}), 400

    try:
        session = Session()
        catch = session.query(Catch).filter_by(photo_url=imageUrl).first()
        session.close()

        if not catch:
            return jsonify({'error': 'No catch found for the provided imageUrl'}), 404

        return jsonify({'detections': catch.exif_data, 'imageUrl': catch.photo_url})
    except Exception as e:
        logging.error(f"Error in get_detections: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/map_fishing_spot', methods=['POST'])
# 추후 Token 관련 데코레이터 추가할 것
def map_fishing_spot():
    session = Session()
    fishing_spots = session.query(FishingPlace).all()
    session.close()

    try:
        locations = [{
            'fishing_place_id': spot.fishing_place_id,
            'name': spot.name,
            'type': spot.type,
            'latitude': spot.latitude,
            'longitude': spot.longitude,
            'address_road': spot.address_road,
            'address_land': spot.address_land,
            'phone_number': spot.phone_number,
            'main_fish_species': spot.main_fish_species,
            'usage_fee': spot.usage_fee,
            'safety_facilities': spot.safety_facilities,
            'convenience_facilities' : spot.convenience_facilities, 
        } for spot in fishing_spots]
        

        return jsonify({
            'message': 'DB호출 완료',
            'location': locations
        })
    except Exception as e:
        return jsonify({f'message : 호출 실패, {e}'}), 401

# Create uploads directory path
AVATAR_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')
if not os.path.exists(AVATAR_UPLOAD_FOLDER):
    os.makedirs(AVATAR_UPLOAD_FOLDER)

# Endpoint to handle avatar upload
@app.route('/profile/avatar', methods=['POST'])
@token_required
def upload_avatar(user_id):
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{user_id}_{uuid.uuid4().hex}.jpg")
        file_path = os.path.join(AVATAR_UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        session = Session()
        try:
            # Query the user within the new session
            current_user = session.query(User).filter_by(user_id=user_id).first()
            if not current_user:
                return jsonify({'error': 'User not found'}), 404

            # Update user's avatar URL
            current_user.avatar = f"/uploads/avatars/{filename}"
            session.commit()
            avatar_url = current_user.avatar
        except Exception as e:
            session.rollback()
            logging.error(f"Error uploading avatar: {e}")
            return jsonify({'error': 'Avatar upload failed'}), 500
        finally:
            session.close()

        return jsonify({'message': 'Avatar uploaded successfully', 'avatarUrl': avatar_url}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
# 요청 위치 기준 가장 가까운 관측소 위치 반환 
@app.route('/backend/closest-sealoc', methods=['POST'])
def get_closest_sealoc():
    user_lat = request.form.get('lat')
    user_lon = request.form.get('lon')

    if user_lat is None or user_lon is None:
        return jsonify({'error': 'Invalid input'}), 400

    session = Session()
    
    ## ST_Distance_Sphere를 사용하여 MySQL에서 직접 거리 계산
    # 조위, 수온, 기온 , 기압 4개 모두 체크 가능한 경우
    query_obsrecent = text("""
        SELECT obs_station_id, obs_post_id, obs_post_name,
            ST_Distance_Sphere(POINT(:lon, :lat), POINT(obs_lon, obs_lat)) AS distance
        FROM TidalObservations
        WHERE obs_object LIKE '%조위%'
            AND obs_object LIKE '%수온%'
            AND obs_object LIKE '%기온%'
            AND obs_object LIKE '%기압%'
        ORDER BY distance ASC
        LIMIT 1;
    """)
    
    # 조수간만 태그 + 없음 제거
    query_obspretab = text("""
        SELECT obs_station_id, obs_post_id, obs_post_name,
            ST_Distance_Sphere(POINT(:lon, :lat), POINT(obs_lon, obs_lat)) AS distance
        FROM TidalObservations
        WHERE obs_object LIKE '%조수간만%'
            AND obs_object NOT LIKE '%없음%'
        ORDER BY distance ASC
        LIMIT 1;
    """)

    try:
        # 두 개의 쿼리 실행
        result_obsrecent = session.execute(query_obsrecent, {'lat': user_lat, 'lon': user_lon}).fetchone()
        result_obspretab = session.execute(query_obspretab, {'lat': user_lat, 'lon': user_lon}).fetchone()

        if result_obsrecent and result_obspretab:
            print(f"obs recent : {result_obsrecent}")
            print(f"obs pretab : {result_obspretab}")
            # 조위 관측소 정보
            obsrecent_data = {
                'obs_station_id': result_obsrecent[0],
                'obs_post_id': result_obsrecent[1],
                'obs_post_name': result_obsrecent[2],
                'distance': result_obsrecent[3] / 1000
            }

            # 조수간만 관측소 정보
            obspretab_data = {
                'obs_station_id': result_obspretab[0],
                'obs_post_id': result_obspretab[1],
                'obs_post_name': result_obspretab[2],
                'distance': result_obspretab[3] / 1000
            }

            # KHOA API 호출
            try:
                api_data = get_sea_weather_by_seapostid({
                    'obsrecent': obsrecent_data['obs_post_id'],
                    'obspretab': obspretab_data['obs_post_id']
                })
                
                # 프론트엔드에 보낼 데이터 구성
                closest_data = {
                    'obsrecent': {
                        **obsrecent_data,
                        'api_response': api_data['obsrecent']
                    },
                    'obspretab': {
                        **obspretab_data,
                        'api_response': api_data['obspretab']
                    }
                }
                return jsonify(closest_data)

            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'API request failed: {e}'}), 500

        else:
            return jsonify({'error': 'No tidal observations found'}), 404

    finally:
        session.close()
        
@app.route('/backend/get-weather', methods=['POST'])
def get_weather_api():
    try:
        # Get and validate coordinates
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        
        if not lat or not lon:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        print(f"lat : {lat}, lon : {lon}")
            
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({'error': 'Invalid coordinate format'}), 400
        
        # Get weather data
        weather_data = get_weather_by_coordinates(lat, lon)
        if not weather_data:
            return jsonify({'error': 'Failed to fetch weather data'}), 500
            
        return jsonify(weather_data)
        
    except Exception as e:
        logging.error(f"Error in get_weather_api: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 애플리케이션 종료 시 세션 제거
@app.teardown_appcontext
def remove_session(exception=None):
    Session.remove()

# Ensure the backend server is running on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)