# 낚시 입문자를 위한 금어종 판별 AI 웹 서비스
![image](https://github.com/user-attachments/assets/ce26f167-06ef-4978-b4bb-d459eeed751b)

# 서버 설정 (/etc/rc.local)
```bash
conda activate pytorch
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

cd /home/ubuntu/Snapish/backend
export FLASK_APP=main.py
flask run --host=0.0.0.0

cd /home/ubuntu/Snapish/frontend
sudo npm run serve
```

# 백엔드
먼저 백엔드 폴더로 이동하세요. `cd backend`. 제공된 `environment.yml`을 사용하여 필요한 패키지가 있는 새로운 conda 환경을 생성하고, 그 다음에 새로 생성된 환경을 활성화하는 것을 권장합니다.

## 콘다 가상환경 없다면
```bash
cd /Snapish/backend
conda env create -n snapish --file environment.yml
conda activate snapish
```
예측 모델의 가중치를 [여기](http://)에서 다운로드하세요. 백엔드에 `models` 폴더를 생성하고 (`mkdir models`), 다운로드한 `*.pth` 파일을 이 디렉토리에 복사하세요.

## 콘다 가상환경 있다면
```bash
cd /Snapish/backend
pip install -r requirements.txt
```

플라스크 앱을 다음과 같이 시작하세요. (윈도우 파워쉘, 백그라운드 작동)
```bash
cd /Snapish/backend
$env:FLASK_APP="main.py"
flask run --host=0.0.0.0 
ps a
```
리눅스 우분투 또는 MAC는 환경설정을 아래와 같이 진행하세요.
```bash
cd /Snapish/backend
export FLASK_APP="main.py"
flask run --host=0.0.0.0
ps a
```

# 프론트엔드
백엔드 폴더에 있는 경우 `cd ../frontend`를 실행하여 프론트엔드 폴더로 이동하세요.
프론트엔드를 설정하고 실행하기 위해서는 node.js가 필요하므로 [여기](https://nodejs.org/en/)의 지침을 따르세요.
이제 필요한 패키지를 다음과 같이 설치하세요 (시간이 좀 걸릴 수 있습니다):
```bash
cd /Snapish/frontend
npm install
```

프론트엔드를 다음과 같이 컴파일하고 실행하세요. (백그라운드 작동)
```bash
cd /Snapish/frontend
npm run serve
ps a
```
