# Osage Chan Discord Bot - 실행 명령어 가이드

## 📋 빠른 실행 가이드

### 1단계: 프로젝트 디렉터리로 이동
```bash
cd /home/dev/Osage_chan_discord_bot
```

### 2단계: 환경 설정 (최초 1회만)
```bash
./setup.sh
```

### 3단계: 봇 실행
```bash
# 방법 1: 직접 실행 (권장)
/home/dev/Osage_chan_discord_bot/.venv/bin/python src/osage_chan/main.py

# 방법 2: run.sh 스크립트 사용
./run.sh

# 방법 3: 가상환경 활성화 후 실행
source .venv/bin/activate
python src/osage_chan/main.py
```

### 4단계: 봇 중지
```
Ctrl + C
```

---

## 🔧 문제 해결 명령어

### 환경변수 확인
```bash
/home/dev/Osage_chan_discord_bot/.venv/bin/python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('BOT_TOKEN:', os.getenv('봇토큰'))"
```

### 패키지 재설치
```bash
/home/dev/Osage_chan_discord_bot/.venv/bin/pip install -r requirements.txt
```

### 가상환경 재생성
```bash
rm -rf .venv venv
./setup.sh
```

---

## 🎵 봇 명령어 (Discord에서 사용)

- `!p [YouTube URL]`: 음악 재생/재생목록 추가
- `!s`: 현재 재생 중인 음악 중지
- `!c`: 재생목록 전체 삭제
- `!r`: 재생목록 첫 번째 곡 삭제

---

## 📝 .env 파일 형식

```
봇토큰=YOUR_DISCORD_BOT_TOKEN
특정유저=123456789,987654321
특정채널=123456789,987654321
```

**주의**: 값에 따옴표를 사용하지 마세요!
