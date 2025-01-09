# 낚시 입문자를 위한 금어종 판별 AI 웹 서비스

[![프로젝트 발표자료](https://github.com/SnapishAgent/Snapish/blob/main/public/presentation-preview.jpg)](https://github.com/SnapishAgent/Snapish/blob/main/public/2%EC%A1%B0%20%ED%8C%8C%EC%9D%B4%EB%84%90%20%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%20%EB%B0%9C%ED%91%9C%EC%9E%90%EB%A3%8C.pdf)

## 1. 백엔드 설정
### 환경 설정
- 백엔드 디렉토리로 이동: `cd backend`
- Conda 환경 생성:
  ```bash
  conda env create -n snapish --file environment.yml
  conda activate snapish
  ```

### 필수 파일 설정
- 모델 파일:
  - [가중치 파일 다운로드](https://drive.google.com/file/d/1wPJOQI87bVANbdyzxKJHHB2N3zZvuqg9/view?usp=drive_link)
  - `models` 폴더 생성 후 `.pth` 파일 복사
- 데이터 파일:
  - [데이터 파일 다운로드](https://drive.google.com/drive/folders/1XaJ8nUDu5BpJc9YafbfTWh_Y3_x5m1-5?usp=drive_link)
  - `data` 폴더 생성 후 `.json` 파일 복사

### 서버 실행
- Windows:
  ```bash
  $env:FLASK_APP="main.py"
  flask run --host=0.0.0.0
  ```

- Mac/Linux:
  ```bash
  export FLASK_APP="main.py"
  flask run --host=0.0.0.0
  ```

## 2. 프론트엔드 설정
### 환경 설정
- Node.js 설치: [다운로드](https://nodejs.org/en/)
- 프론트엔드 디렉토리로 이동: `cd frontend`
- 패키지 설치:
  ```bash
  npm install
  ```

### 실행
- 개발 서버 시작:
  ```bash
  npm run serve
  ```
