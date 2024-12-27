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
    Enum,
    Boolean,
    Text,
    DECIMAL,
    JSON,
    Float,
    VARCHAR,
    text,
    func
)
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from services.weather_service import get_sea_weather_by_seapostid, get_weather_by_coordinates
from services.lunar_mulddae import get_mulddae_cycle, calculate_moon_phase
from services.initialize_db import initialize_service
from services.openai_assistant import assistant_talk_request, assistant_talk_get
from ultralytics import YOLO
from flask_cors import CORS

# Ensure the 'uploads' directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """
    Check if the file has one of the allowed extensions.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 환경 변수 로드
load_dotenv("./backend/.env")

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
    weight_kg = Column(DECIMAL(10, 3), nullable=True)  # 무게(kg)
    length_cm = Column(DECIMAL(10, 2), nullable=True)  # 길이(cm)
    latitude = Column(DECIMAL(10, 8), nullable=True)  # 위도
    longitude = Column(DECIMAL(11, 8), nullable=True)  # 경도
    memo = Column(Text, nullable=True)  # 메모

    user = relationship('User', back_populates='catches')
    location = relationship('Location', back_populates='catches')  # Existing line
    species = relationship('FishSpecies', back_populates='catches')  # Existing line
    tournament_participants = relationship('TournamentParticipant', back_populates='catch')  # Add this line
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIConsent(Base):
    __tablename__ = 'AIConsent'

    consent_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime, default=datetime.utcnow)  # 동의 날짜 추가
    consent_type = Column(String(50))  # 동의 유형 추가 (예: 'fish_data', 'privacy')
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
    images = Column(JSON, default=list)  # Store multiple image URLs as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='posts')
    likes = relationship('PostLike', back_populates='post', cascade='all, delete')
    comments = relationship('PostComment', back_populates='post', cascade='all, delete')
    retweets = relationship('PostRetweet', back_populates='post', cascade='all, delete')


class PostLike(Base):
    __tablename__ = 'PostLikes'

    like_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('CommunicationBoard.post_id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship('CommunicationBoard', back_populates='likes')
    user = relationship('User')


class PostComment(Base):
    __tablename__ = 'PostComments'

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('CommunicationBoard.post_id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    post = relationship('CommunicationBoard', back_populates='comments')
    user = relationship('User')


class PostRetweet(Base):
    __tablename__ = 'PostRetweets'

    retweet_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('CommunicationBoard.post_id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('Users.user_id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship('CommunicationBoard', back_populates='retweets')
    user = relationship('User')


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

baseUrl = os.getenv('BASE_URL')

# Flask 앱 초기화
app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": [f'{baseUrl}:5000', f'{baseUrl}:8080'],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}}, supports_credentials=True)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = YOLO(f'./models/{os.getenv("MODEL_NAME")}').to(device)

# 초시 헤더를 한 after_request 데코레이터를 앱 초기화 직후에 추가
@app.after_request
def add_header(response):
    if request.path.startswith('/uploads/'):
        response.cache_control.max_age = 31536000  # 1년
        response.cache_control.public = True
    return response

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

CONF_SCORE = 0.5

# REST API
@app.route('/')
def hello():
    return 'Welcome to SNAPISH'

# 물떼 정보 받아오기
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

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  # 실 서비스에서는 안전 키로 변경하세요.

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

    return jsonify({'message': '회원가입이 성공적으로 완료되었습니다.'}), 201

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

# 이미지 최적화 함수 추가
def optimize_image(image, max_size=1024):
    """Optimize image size and quality for mobile"""
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Convert to RGB if necessary
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    
    # Optimize
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=85, optimize=True)
    buffer.seek(0)
    return buffer

# predict 라트 수정
@app.route('/backend/predict', methods=['POST'])
def predict():
    try:
        if 'image' in request.files:
            file = request.files['image']
            # 파일 이름이 비어있는지 먼저 확인
            if file.filename == '':
                return jsonify({
                    'error': 'invalid_file_name',
                    'message': '파일이 선택되지 않았습니다.'
                }), 400
                
            # 파일 타입 검증
            if not allowed_file(file.filename):
                return jsonify({
                    'error': 'invalid_file_type',
                    'message': '지원하지 않는 파일 형식입니다.'
                }), 400
                
            try:
                img = Image.open(file.stream).convert('RGB')
            except Exception as e:
                return jsonify({
                    'error': 'invalid_file_open',
                    'message': '이미지를 처리할 수 없습니다.'
                }), 400
        else:
            try:
                data = request.get_json()
                image_base64 = data.get('image_base64')
                if not image_base64:
                    return jsonify({                   
                                    'error': 'invalid_image_formatting_error',
                                    'message': '업로드 이미지를 변환하는 중 오류가 발생했습니다.'
                                    }), 400
                image_data = base64.b64decode(image_base64)
                img = Image.open(io.BytesIO(image_data)).convert('RGB')
            except Exception as e:
                ({                   
                    'error': 'invalid_image_open',
                    'message': '업로드 이미지를 열지 못했습니다.'
                    }), 400

        # 이미지 최적화
        optimized_buffer = optimize_image(img)
        img = Image.open(optimized_buffer)

        results = model(img, exist_ok=True, device=device)
        detections = []
        
        for result in results:  # Iterate over results
            for cls, conf, bbox in zip(result.boxes.cls, result.boxes.conf, result.boxes.xyxy):
                if float(conf) > CONF_SCORE:
                    detections.append({
                        'label': labels_korean.get(int(cls), '알 수 없는 라벨'),
                        'confidence': float(conf),
                        'prohibited_dates': PROHIBITED_DATES.get(labels_korean.get(int(cls), ''), ''),
                        'bbox': bbox.tolist()
                    })
                    
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        if detections:
            try:
                top_fish = detections[0]['label']
                assistant_request_id = assistant_talk_request(f"{top_fish}")
            
            except Exception as e:
                print(f"assistant_request_id 호출 실패 : {e}")
                assistant_request_id = None

        # 감지 결과가 없거나 모든 결과의 정확도가 낮은 경우
        if not detections:
            return jsonify({
                'error': 'detection_failed',
                'errorType': 'no_detection' if not results[0].boxes.cls.size(0) else 'low_confidence',
                'message': '물고기를 감지할 수 없습니다.' if not results[0].boxes.cls.size(0) else '물고기를 정확하게 인식할 수 없습니다.'
            }), 200  # 프론트엔드 처리를 위해 200 반환

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
            # Check if catchId is provided in the request
            catch_id = request.args.get('catchId')
            if catch_id:
                # Update existing catch
                existing_catch = session.query(Catch).filter_by(catch_id=catch_id, user_id=current_user.user_id).first()
                if existing_catch:
                    existing_catch.exif_data = detections
                    existing_catch.photo_url = filename
                    existing_catch.catch_date = datetime.utcnow()
                    session.commit()
                    response_data = {
                        'id': existing_catch.catch_id,
                        'detections': detections,
                        'imageUrl': filename
                    }
                else:
                    return jsonify({'error': 'Catch not found'}), 404
            else:
                # Save new catch
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
                    'imageUrl': filename,
                    'assistant_request_id': assistant_request_id
                }
        else:
            # Do not save the image to disk or database
            buffered = io.BytesIO()
            img.save(buffered, format='JPEG')
            img_str = base64.b64encode(buffered.getvalue()).decode()
            response_data = {
                'detections': detections,
                'image_base64': img_str,
                'assistant_request_id': assistant_request_id
            }

        session.close()
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({'error': '이미지 처리 중 오류가 발생했습니다.'}), 500
    
@app.route('/backend/chat/<thread_id>/<run_id>', methods=['GET'])
def assistant_talk_result(thread_id, run_id):
    try:
        formatted_text = assistant_talk_get(thread_id, run_id)
        
        if not formatted_text:
            return jsonify({            
                'data': None,
                'status': 'No response from assistant'
            }), 404
            
        return jsonify({
            'data': formatted_text,
            'status': 'Success'
        })
        
    except TimeoutError:
        return jsonify({
            'data': None,
            'status': 'Assistant response timed out'
        }), 408
    except Exception as e:
        return jsonify({
            'data': None,
            'status': f'Internal server error : {e}'
        }), 500

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

    # 최근 동을 회하는 로직 (예: 데이터베이스에서 최근 5개 캐치를 가져오기)
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
def create_catch(user_id):
    data = request.get_json()
    session = Session()
    try:
        new_catch = Catch(
            user_id=user_id,
            photo_url=data.get('imageUrl'),
            exif_data=data.get('detections'),
            catch_date=datetime.strptime(data.get('catch_date'), '%Y-%m-%d')
        )
        session.add(new_catch)
        session.commit()
        
        return jsonify({
            'id': new_catch.catch_id,
            'imageUrl': new_catch.photo_url,
            'detections': new_catch.exif_data,
            'catch_date': new_catch.catch_date.strftime('%Y-%m-%d'),
            'weight_kg': float(new_catch.weight_kg) if new_catch.weight_kg else None,
            'length_cm': float(new_catch.length_cm) if new_catch.length_cm else None,
            'latitude': float(new_catch.latitude) if new_catch.latitude else None,
            'longitude': float(new_catch.longitude) if new_catch.longitude else None,
            'memo': new_catch.memo,
            'message': '치가 성공적으로 추가되었습니다.'
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/catches', methods=['GET'])
@token_required
def get_catches(user_id):
    session = Session()
    try:
        current_user = session.query(User).filter_by(user_id=user_id).first()
        if not current_user:
            return jsonify({'message': 'User not found'}), 404

        catches = session.query(Catch).filter_by(user_id=current_user.user_id).all()
        
        # 모든 필요한 데이터를 포함하여 반환
        return jsonify([{
            'id': catch.catch_id,
            'imageUrl': catch.photo_url,
            'detections': catch.exif_data,
            'catch_date': catch.catch_date.strftime('%Y-%m-%d'),
            'weight_kg': float(catch.weight_kg) if catch.weight_kg else None,
            'length_cm': float(catch.length_cm) if catch.length_cm else None,
            'latitude': float(catch.latitude) if catch.latitude else None,
            'longitude': float(catch.longitude) if catch.longitude else None,
            'memo': catch.memo
        } for catch in catches])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/catches/<int:catch_id>', methods=['PUT'])
@token_required
def update_catch(user_id, catch_id):
    data = request.get_json()
    session = Session()
    try:
        catch = session.query(Catch).filter_by(catch_id=catch_id, user_id=user_id).first()
        if not catch:
            session.close()
            return jsonify({'error': 'Catch not found'}), 404

        # 데이터 유효성 검사
        try:
            if 'weight_kg' in data:
                weight = float(data['weight_kg']) if data['weight_kg'] is not None else None
                if weight is not None and (weight < 0 or weight > 999.999):
                    return jsonify({'error': 'Weight must be between 0 and 999.999 kg'}), 400
                catch.weight_kg = weight

            if 'length_cm' in data:
                length = float(data['length_cm']) if data['length_cm'] is not None else None
                if length is not None and (length < 0 or length > 999.99):
                    return jsonify({'error': 'Length must be between 0 and 999.99 cm'}), 400
                catch.length_cm = length

            if 'latitude' in data:
                lat = float(data['latitude']) if data['latitude'] is not None else None
                if lat is not None and (lat < -90 or lat > 90):
                    return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
                catch.latitude = lat

            if 'longitude' in data:
                lon = float(data['longitude']) if data['longitude'] is not None else None
                if lon is not None and (lon < -180 or lon > 180):
                    return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
                catch.longitude = lon
        except ValueError:
            return jsonify({'error': 'Invalid numeric value provided'}), 400

        # Update existing fields
        if 'detections' in data:
            catch.exif_data = data['detections']
        if 'catch_date' in data:
            catch.catch_date = datetime.strptime(data['catch_date'], '%Y-%m-%d')
        if 'memo' in data:
            catch.memo = data['memo']

        session.commit()
        return jsonify({
            'id': catch.catch_id,
            'imageUrl': catch.photo_url,
            'detections': catch.exif_data,
            'catch_date': catch.catch_date.strftime('%Y-%m-%d'),
            'weight_kg': float(catch.weight_kg) if catch.weight_kg else None,
            'length_cm': float(catch.length_cm) if catch.length_cm else None,
            'latitude': float(catch.latitude) if catch.latitude else None,
            'longitude': float(catch.longitude) if catch.longitude else None,
            'memo': catch.memo
        })
    except Exception as e:
        session.rollback()
        logging.error(f"Error updating catch: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

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
    response = send_from_directory('uploads', filename)
    # 캐시 컨트롤 헤더 추가
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1년
    response.headers['Vary'] = 'Accept-Encoding'
    return response

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
# 추후 Token 관련 데코레이터 ��가할 것
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
    
# 요청 위치 기준 가장 가까운 관 위치 반환 
@app.route('/backend/closest-sealoc', methods=['POST'])
def get_closest_sealoc():
    user_lat = request.form.get('lat')
    user_lon = request.form.get('lon')

    if user_lat is None or user_lon is None:
        return jsonify({'error': 'Invalid input'}), 400

    session = Session()
    
    ## ST_Distance_Sphere를 사용하여 MySQL에 직접 거리 계산
    # 조위, 수온, 기온 , 기압 4개 모두 체 가능한 우
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
    
    # 조수간 태그 + 없음 제거
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
        #  개 쿼리 실행
        result_obsrecent = session.execute(query_obsrecent, {'lat': user_lat, 'lon': user_lon}).fetchone()
        result_obspretab = session.execute(query_obspretab, {'lat': user_lat, 'lon': user_lon}).fetchone()

        if result_obsrecent and result_obspretab:
            print(f"obs recent : {result_obsrecent}")
            print(f"obs pretab : {result_obspretab}")
            # 조위 관측 정보
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

@app.route('/api/consent/check', methods=['GET'])
@token_required
def check_consent(user_id):
    session = Session()
    try:
        consent = session.query(AIConsent).filter_by(user_id=user_id).first()
        return jsonify({
            'hasConsent': bool(consent and consent.consent_given),
            'lastConsentDate': consent.consent_date.isoformat() if consent else None
        })
    finally:
        session.close()

@app.route('/api/consent', methods=['POST'])
@token_required
def update_consent(user_id):
    data = request.get_json()
    consent_given = data.get('consent', False)
    
    session = Session()
    try:
        consent = session.query(AIConsent).filter_by(user_id=user_id).first()
        if consent:
            consent.consent_given = consent_given
            consent.consent_date = datetime.utcnow()
        else:
            consent = AIConsent(
                user_id=user_id,
                consent_given=consent_given,
                consent_date=datetime.utcnow()
            )
            session.add(consent)
        session.commit()
        return jsonify({'message': 'Consent updated successfully'})
    finally:
        session.close()

# 서비스 목록 API 추가
@app.route('/api/services', methods=['GET'])
def get_services():
    # 기본 서비스 목록 반환
    services = [
        {
            "id": 1,
            "name": "물때 정보",
            "icon": "/icons/tide.png",
            "route": "/map-location-service"
        },
        {
            "id": 2,
            "name": "날씨 정보",
            "icon": "/icons/weather.png",
            "route": "/map-location-service"
        },
        {
            "id": 3,
            "name": "내 기록",
            "icon": "/icons/record.png",
            "route": "/catches"
        },
        {
            "id": 4,
            "name": "커뮤니티",
            "icon": "/icons/community.png",
            "route": "/community"
        },
        # 추가 서비스들...
    ]
    return jsonify(services)

def get_full_url(url):
    if not url:
        return None
    if url.startswith('http'):
        return url
    return f"{baseUrl}{url}"


@app.route('/api/posts', methods=['GET'])
@token_required
def get_posts(user_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        session = Session()
        
        # Calculate total posts and pages
        total = session.query(CommunicationBoard).count()
        offset = (page - 1) * per_page
        
        # Get posts with pagination
        posts = session.query(CommunicationBoard)\
            .order_by(CommunicationBoard.created_at.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()
            
        result = []
        for post in posts:
            user = session.query(User).get(post.user_id)
            
            # Get like status for current user
            is_liked = session.query(PostLike)\
                .filter_by(post_id=post.post_id, user_id=user_id)\
                .first() is not None
            
            post_data = {
                'post_id': post.post_id,
                'user_id': post.user_id,
                'username': user.username if user else 'Unknown',
                'avatar': get_full_url(user.avatar) if user and user.avatar else None,
                'title': post.title,
                'content': post.content,
                'images': [get_full_url(image) for image in (post.images or [])],
                'created_at': post.created_at.isoformat(),
                'likes_count': session.query(PostLike).filter_by(post_id=post.post_id).count(),
                'comments_count': session.query(PostComment).filter_by(post_id=post.post_id).count(),
                'is_liked': is_liked
            }
            result.append(post_data)
            
        total_pages = (total + per_page - 1) # per_page
        
        return jsonify({
            'posts': result,
            'total': total,
            'pages': total_pages,
            'current_page': page
        })
    except Exception as e:
        logging.error(f"Error getting posts: {str(e)}")
        return jsonify({'error': '게시물을 불러오는 중 오류가 발생했습니다.'}), 500
    finally:
        session.close()

@app.route('/api/posts', methods=['POST'])
@token_required
def create_post(user_id):
    session = Session()
    try:
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        images = request.files.getlist('images')

        if not title or not content:
            return jsonify({'error': '제목과 내용은 필수입니다.'}), 400

        # Create new post
        new_post = CommunicationBoard(
            user_id=user_id,
            title=title,
            content=content,
            images=[],  # Initialize empty list for images
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Handle image uploads
        for image in images:
            if image and allowed_file(image.filename):
                try:
                    filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
                    image_path = os.path.join(UPLOAD_FOLDER, filename)
                    image.save(image_path)
                    new_post.images.append(f'/uploads/{filename}')
                except Exception as e:
                    logging.error(f"Error saving image {image.filename}: {str(e)}")
                    continue

        session.add(new_post)
        session.commit()

        # Get user info for response
        user = session.query(User).get(user_id)

        response_data = {
            'message': '게시물이 성공적으로 작성되었습니다.',
            'post': {
                'post_id': new_post.post_id,
                'user_id': user_id,
                'username': user.username,
                'avatar': get_full_url(user.avatar),
                'title': new_post.title,
                'content': new_post.content,
                'images': [get_full_url(url) for url in new_post.images],
                'created_at': new_post.created_at.isoformat(),
                'updated_at': new_post.updated_at.isoformat(),
                'likes_count': 0,
                'comments_count': 0,
                'is_liked': False
            }
        }
        return jsonify(response_data), 201

    except Exception as e:
        session.rollback()
        logging.error(f"Error creating post: {str(e)}")
        return jsonify({'error': '게시물 작성 중 오류가 발생했습니다.'}), 500
    finally:
        session.close()

@app.route('/api/posts/<int:post_id>', methods=['GET'])
@token_required
def get_post(user_id, post_id):
    session = Session()
    try:
        post = session.query(CommunicationBoard).get(post_id)
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없습니다.'}), 404

        user = session.query(User).get(post.user_id)
        if not user:
            return jsonify({'error': '게시물 작성자를 찾을 수 없습니다.'}), 500

        # Check if the current user has liked this post
        is_liked = session.query(PostLike).filter_by(
            post_id=post_id,
            user_id=user_id
        ).first() is not None

        # Get counts
        likes_count = session.query(PostLike).filter_by(post_id=post_id).count()
        comments_count = session.query(PostComment).filter_by(post_id=post_id).count()

        # Handle images safely
        images = []
        if post.images:
            if isinstance(post.images, list):
                images = [get_full_url(image) for image in post.images]
            else:
                logging.warning(f"Unexpected images type for post {post_id}: {type(post.images)}")
                images = []

        response_data = {
            'post_id': post.post_id,
            'user_id': post.user_id,
            'username': user.username,
            'avatar': get_full_url(user.avatar),
            'title': post.title,
            'content': post.content,
            'images': images,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat() if post.updated_at else post.created_at.isoformat(),
            'likes_count': likes_count,
            'comments_count': comments_count,
            'is_liked': is_liked
        }

        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error getting post {post_id}: {str(e)}")
        return jsonify({'error': '게시물을 불러오는 중 오류가 발생했습니다.'}), 500
    finally:
        session.close()

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(user_id, post_id):
    session = Session()
    try:
        post = session.query(CommunicationBoard).filter_by(post_id=post_id, user_id=user_id).first()
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없거나 수정 권한이 없습니다.'}), 404

        data = request.form
        new_images = request.files.getlist('images')
        removed_images = request.form.getlist('removed_images[]')

        # Initialize images list if it doesn't exist
        if not hasattr(post, 'images') or post.images is None:
            post.images = []
        elif not isinstance(post.images, list):
            post.images = []

        # Handle removed images
        if removed_images:
            logging.info(f"Removing images: {removed_images}")
            for image_url in removed_images:
                if image_url in post.images:
                    try:
                        post.images.remove(image_url)
                        # Delete the actual file
                        image_path = os.path.join(app.root_path, image_url.lstrip('/'))
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            logging.info(f"Deleted file: {image_path}")
                    except Exception as e:
                        logging.error(f"Error removing image {image_url}: {str(e)}")

        # Add new images
        for image in new_images:
            if image and allowed_file(image.filename):
                try:
                    filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
                    image_path = os.path.join(UPLOAD_FOLDER, filename)
                    image.save(image_path)
                    post.images.append(f'/uploads/{filename}')
                    logging.info(f"Added new image: {filename}")
                except Exception as e:
                    logging.error(f"Error saving image {image.filename}: {str(e)}")

        # Update post content
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.updated_at = datetime.utcnow()

        session.commit()
        
        # Prepare response with updated data
        response_data = {
            'message': '게시물이 성공적으로 수정되었습니다.',
            'post': {
                'post_id': post.post_id,
                'title': post.title,
                'content': post.content,
                'images': [get_full_url(url) for url in (post.images or [])],
                'updated_at': post.updated_at.isoformat()
            }
        }
        logging.info(f"Successfully updated post {post_id} with images: {post.images}")
        return jsonify(response_data)

    except Exception as e:
        session.rollback()
        logging.error(f"Error updating post {post_id}: {str(e)}")
        return jsonify({'error': '게시물 수정 중 오류가 발생했습니다.'}), 500
    finally:
        session.close()

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(user_id, post_id):
    session = Session()
    try:
        post = session.query(CommunicationBoard).filter_by(post_id=post_id, user_id=user_id).first()
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없거나 삭제 권한이 없습니다.'}), 404

        # Delete all associated images
        if post.images:
            for image_url in post.images:
                image_path = os.path.join(UPLOAD_FOLDER, os.path.basename(image_url))
                if os.path.exists(image_path):
                    os.remove(image_path)

        session.delete(post)
        session.commit()

        return jsonify({'message': '게시물이 성공적으로 삭제되었습니다.'})
    except Exception as e:
        session.rollback()
        logging.error(f"Error deleting post: {str(e)}")
        return jsonify({'error': '게시물 삭제 중 오류가 발생했습니다.'}), 500
    finally:
        session.close()

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@token_required
def toggle_like(user_id, post_id):
    session = Session()
    try:
        # Check if post exists
        post = session.query(CommunicationBoard).get(post_id)
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없습니다.'}), 404

        # Check if user already liked the post
        existing_like = session.query(PostLike).filter_by(
            post_id=post_id,
            user_id=user_id
        ).first()

        if existing_like:
            # Unlike
            session.delete(existing_like)
            session.commit()
            likes_count = session.query(PostLike).filter_by(post_id=post_id).count()
            return jsonify({
                'message': '좋아요가 취소되었습니다.',
                'is_liked': False,
                'likes_count': likes_count
            })
        else:
            # Like
            new_like = PostLike(post_id=post_id, user_id=user_id)
            session.add(new_like)
            session.commit()
            likes_count = session.query(PostLike).filter_by(post_id=post_id).count()
            return jsonify({
                'message': '좋아요가 추가되었습니다.',
                'is_liked': True,
                'likes_count': likes_count
            })

    except Exception as e:
        session.rollback()
        logging.error(f"Error toggling like for post {post_id}: {str(e)}")
        return jsonify({'error': '좋아요 처리 중 오류가 발생했습니다.'}), 500
    finally:
        session.close()

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
@token_required
def get_comments(user_id, post_id):
    session = Session()
    try:
        # Check if post exists
        post = session.query(CommunicationBoard).get(post_id)
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없습니다.'}), 404

        # Get comments with user information
        comments = session.query(PostComment, User).join(
            User, PostComment.user_id == User.user_id
        ).filter(
            PostComment.post_id == post_id
        ).order_by(
            PostComment.created_at.desc()
        ).all()

        comments_data = [{
            'comment_id': comment.comment_id,
            'user_id': comment.user_id,
            'username': user.username,
            'avatar': get_full_url(user.avatar),
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        } for comment, user in comments]

        return jsonify({'comments': comments_data})

    except Exception as e:
        logging.error(f"Error getting comments for post {post_id}: {str(e)}")
        return jsonify({'error': '댓글을 불러오는 중 오류가 발생했습니다.'}), 500
    finally:
        session.close()

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(user_id, post_id):
    session = Session()
    try:
        # Check if post exists
        post = session.query(CommunicationBoard).get(post_id)
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없습니다.'}), 404

        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'error': '댓글 내용이 필요합니다.'}), 400

        # Create new comment
        new_comment = PostComment(
            post_id=post_id,
            user_id=user_id,
            content=data['content']
        )
        session.add(new_comment)
        session.commit()

        # Get user info for response
        user = session.query(User).get(user_id)
        
        comment_data = {
            'comment_id': new_comment.comment_id,
            'user_id': user_id,
            'username': user.username,
            'avatar': get_full_url(user.avatar),
            'content': new_comment.content,
            'created_at': new_comment.created_at.isoformat()
        }

        return jsonify({
            'message': '댓글이 성공적으로 작성되었습니다.',
            'comment': comment_data
        })

    except Exception as e:
        session.rollback()
        logging.error(f"Error creating comment for post {post_id}: {str(e)}")
        return jsonify({'error': '댓글 작성 중 오류가 발생했습니다.'}), 500
    finally:
        session.close()

@app.route('/api/posts/top', methods=['GET'])
def get_top_posts():
    session = Session()
    try:
        # Get top 5 posts by likes
        top_posts = session.query(CommunicationBoard)\
            .outerjoin(PostLike)\
            .group_by(CommunicationBoard.post_id)\
            .order_by(func.count(PostLike.like_id).desc(), CommunicationBoard.created_at.desc())\
            .limit(5)\
            .all()

        if not top_posts:
            # If no posts with likes, get the most recent 5 posts
            top_posts = session.query(CommunicationBoard)\
                .order_by(CommunicationBoard.created_at.desc())\
                .limit(5)\
                .all()

        result = []
        for post in top_posts:
            user = session.query(User).get(post.user_id)
            post_data = {
                'post_id': post.post_id,
                'user_id': post.user_id,
                'username': user.username if user else 'Unknown',
                'avatar': get_full_url(user.avatar) if user else None,
                'title': post.title,
                'content': post.content,
                'images': [get_full_url(image) for image in (post.images or [])],
                'created_at': post.created_at.isoformat(),
                'likes_count': session.query(PostLike).filter_by(post_id=post.post_id).count(),
                'comments_count': session.query(PostComment).filter_by(post_id=post.post_id).count(),
            }
            result.append(post_data)

        return jsonify(result)
    except Exception as e:
        logging.error(f"Error getting top posts: {str(e)}")
        return jsonify({'error': 'Error fetching top posts'}), 500
    finally:
        session.close()
        
    # 애플리케이션 종료 시 세 제거
@app.teardown_appcontext
def remove_session(exception=None):
    Session.remove()

# Ensure the backend server is running on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)