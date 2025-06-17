# 🎣 낚시 입문자를 위한 금어기 판별 AI 웹 서비스

[![프로젝트 발표자료](https://github.com/SnapishAgent/Snapish/blob/main/public/presentation-preview.jpg)](https://github.com/SnapishAgent/Snapish/blob/main/public/2%EC%A1%B0%20%ED%8C%8C%EC%9D%B4%EB%84%90%20%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%20%EB%B0%9C%ED%91%9C%EC%9E%90%EB%A3%8C.pdf)
> 메인 이미지 클릭 시, 프로젝트 발표 자료로 이동됩니다!

## 🔍 프로젝트 개요
Snapish는 대한민국 1,000만 낚시인들을 위한 딥러닝 기반 금어종 판별 시스템입니다. 국립수산과학원의 [금어기·금지체장 정보](https://www.nifs.go.kr/contents/actionContentsCons0148.do)를 기반으로 개발되었으며, 낚시 종사자들의 법규 준수와 해양 생태계 보호를 지원합니다. 현재 17개 어종에 대해 88%(mAP50)의 탐지 정확도를 달성했으며, 인공지능 모델 레이어 개선과 사용자 참여형 데이터 수집을 통해 97% 이상의 정확도 달성을 목표로 하고 있습니다.

## 📌 프로젝트 정보
- **기간**: 2024.12.03 ~ 2025.01.02 (평일 26일)
- **인원**: 4인
- **역할**
  - 👑 AI 모델 개발
  - 💻 백엔드 개발
  - 🎨 프론트엔드 개발
  - 📊 DB 설계 및 데이터 수집
 
## ✨ 주요 기능
- 🔍 17개 주요 금어기 판별 기능 제공
- 📖 어종별 특징 및 금지체장 가이드라인 제공
- 📝 내가 잡은 물고기 리스팅 기록 시스템 제공
- 🌊 오늘의 낚시 스팟 및 물떼/날씨 정보 제공
- 👥 사용자 참여형 데이터 수집 시스템

## ⚙️ 핵심 기술 스택

### 🤖 AI/ML
- **객체 탐지 엔진**: Ultralytics YOLOv11
  - 커스텀 데이터셋 기반 전이학습 구현
- **데이터셋 관리**: Roboflow
  - 1,500+ 이미지 데이터 전처리 및 증강
- **이미지 생성 AI**: OpenAI, Robobrush, ideogram
  - 프로젝트 이미지 및 UI 리소스 생성

### 🔧 백엔드 아키텍처
- **웹 프레임워크**: Flask `v3.1.0`
  - RESTful API 설계
  - 비동기 이미지 처리 파이프라인 구현
- **데이터베이스**: MySQL Server `v8.0`
  - 캐싱 레이어 구현으로 응답 속도 최적화

### 🎨 프론트엔드 아키텍처
- **런타임**: Node.js `v20.15.1`
- **프레임워크**: Vue.js `v3.5.13`
  - 실시간 이미지 처리 결과 시각화

## 🐟 탐지 가능 어종

### 해수어 (11종)
- 감성돔, 대구, 갈치
- 말쥐치, 넙치, 조피볼락
- 삼치, 문치가자미, 돌돔
- 참돔, 옥돔

### 갑각류 및 연체동물 (6종)
- 꽃게, 대게
- 참문어, 낙지, 주꾸미, 살오징어

> 각 어종별 금어기 및 금지체장 정보는 국립수산과학원 기준을 준수합니다.

## 🚀 시스템 구축 가이드

### 1️⃣ 백엔드 환경 구성
```bash
cd backend
conda env create -n snapish --file environment.yml
conda activate snapish
```

### 2️⃣ 모델 및 데이터 설정
> 필수 리소스

- 📦 [AI 모델 가중치 파일](https://drive.google.com/file/d/1wPJOQI87bVANbdyzxKJHHB2N3zZvuqg9/view?usp=drive_link) → `/backend/models/`
- 📍 [지역별 낚시터 메타데이터](https://drive.google.com/drive/folders/1XaJ8nUDu5BpJc9YafbfTWh_Y3_x5m1-5?usp=drive_link) → `/backend/data/`
- 📊 [학습 데이터셋](https://drive.google.com/drive/folders/17KH-xu6vKP_P100asU2G-P0ma_Pf8Zd5?usp=drive_link) → `/backend/data/`
- 🔬 [모델 학습 프로세스](https://www.kaggle.com/code/twoimo/yolo11-fish-transfer-learning) → `/backend/`

### 3️⃣ 서비스 실행

#### 데이터베이스 설정
```bash
# MySQL 서버 실행 확인
mysql -u root -p
# 데이터베이스 생성
CREATE DATABASE snapish;
# 데이터베이스 사용자 설정
GRANT ALL PRIVILEGES ON snapish.* TO 'snapish_user'@'localhost' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;
```

#### 포트 설정
```bash
# 백엔드 포트 설정 (.env 파일)
# 프론트엔드 포트 설정 (vue.config.js, .env)
```

#### 백엔드 서버 실행:
```bash
# Windows
cd backend
$env:FLASK_APP="main.py"
flask run --host=0.0.0.0 --port=5000

# Mac/Linux
cd backend
export FLASK_APP="main.py"
flask run --host=0.0.0.0 --port=5000
```

#### 프론트엔드 개발 서버 실행:
```bash
cd frontend
npm install
npm run serve
```

#### 서비스 접속
서비스 실행 후, Google Chrome 브라우저를 열고 다음 URL로 접속하세요:
```
http://localhost:80/
```
> 💡 백엔드 서버(5000번 포트)와 프론트엔드 서버(80번 포트)가 모두 정상 작동해야 서비스가 정상적으로 동작합니다.

## 📈 성과 및 향후 계획

### 🏆 현재 성과
- 17개 어종 대상 식별 정확도 88% 달성 (mAP50)
- 전국 낚시터 약 2,000개 이상의 데이터베이스 구축

### 🎯 개선 계획
- 인공지능 모델 성능 개선 (Self-supervised learning, Vision transformer)
- 사용자 참여형 데이터 수집으로 정확도 95% 이상 달성
- 탐지 가능한 물고기 어종 확대 (30종 이상, 바다 고기, 민물 고기 등)
- 실시간 낚시터 정보 공유 커뮤니티 기능 구현
- 낚시터 스토어 및 선박 사전 예약 기능 구현

### 🌏 사회적 기여
- 불법 어획 방지를 통한 해양 생태계 보호
- 1,000만 낚시인의 준법 조업 지원

## 📚 참고 자료
- [국립수산과학원 금어기•금지체장 정보](https://www.nifs.go.kr/contents/actionContentsCons0148.do)
- [낚시꾼 1천만명 시대…부산서 낚시산업 활성화 토론회](https://www.yna.co.kr/view/AKR20240906025800051)
