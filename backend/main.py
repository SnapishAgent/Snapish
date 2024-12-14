import os
import logging
import random
import pandas as pd
import numpy as np

from scipy import spatial
from dotenv import load_dotenv
from datetime import datetime

from services.weather_service import get_weather_by_coordinates
from services.location_service import get_location_by_coordinates
from services.lunar_mulddae import get_mulddae_cycle, calculate_moon_phase

from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image
import torch
import io

# INIT
# project_dir = os.path.dirname(os.path.abspath(__file__))
# database_file = "sqlite:///{}".format(os.path.join(project_dir, "test.db"))

app = Flask(__name__)
CORS(app)  # 모든 도메인에서의 요청을 허용
# app.config['SQLALCHEMY_DATABASE_URI'] = database_file
# db = SQLAlchemy(app)
# logging.basicConfig(level=logging.INFO)

# 모델 로드
model = YOLO('./models/yolo11m_ep50_confi91_predict.pt')  # 모델 경로 지정

# 라벨 매핑 (영어 -> 한국어)
labels_korean = {
    0: '넙치',
    1: '조피볼락',
    2: '참돔',
    3: '감성돔',
    4: '돌돔'
}

# REST API
@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Welcome to Pic2Prof'
        
@app.route('/backend/mulddae', methods=['POST'])
def get_mulddae():
    if request.method == 'POST':
        now_date = request.form.get('nowdate')
        print(f"HERE! {now_date}")
        if not now_date:
            return jsonify({"error": "The 'nowdate' parameter is required"}), 400

        try:
            # 날짜 형식 확인
            try:
                parsed_date = datetime.strptime(now_date, "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

            # 물때 정보 계산
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
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500
            
@app.route('/backend/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': '이미지가 업로드되지 않았습니다.'}), 400

    file = request.files['image']
    img_bytes = file.read()

    try:
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')  # RGB로 변환
    except Exception as e:
        return jsonify({'error': '이미지 파일을 열 수 없습니다.'}), 400

    # 모델 예측
    results = model(img, exist_ok=True, device='cuda' if torch.cuda.is_available() else 'cpu')  # GPU 사용 가능 시 GPU로 설정

    # 예측 결과에서 라벨 및 신뢰도 추출 및 한국어로 치환
    detections = []
    for result in results:
        for cls, conf in zip(result.boxes.cls, result.boxes.conf):
            cls_int = int(cls)
            korean_label = labels_korean.get(cls_int, '알 수 없는 라벨')
            confidence = float(conf)
            detections.append({
                'label': korean_label,
                'confidence': confidence
            })
    print("detections before sorting: ", detections)

    # 신뢰도 순으로 정렬 (높은 신뢰도 먼저)
    detections.sort(key=lambda x: x['confidence'], reverse=True)
    print("detections after sorting: ", detections)

    # 후보군이 없을 경우 '알 수 없음'으로 설정
    if not detections:
        detections.append({
            'label': '알 수 없음',
            'confidence': 0.0
        })
        print("No detections found. Appended '알 수 없음'.")

    return jsonify({'detections': detections})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)