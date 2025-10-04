# Osage Chan Discord Bot

한글 TTS와 음악 재생 기능을 제공하는 디스코드 봇입니다.

---

## 설치 및 실행

### 1. 환경 설정
```bash
# 프로젝트 디렉터리로 이동
cd /home/dev/Osage_chan_discord_bot

# setup 스크립트 실행 (가상환경 생성 및 패키지 설치)
./setup.sh
```

### 2. 환경변수 설정
`.env` 파일에서 다음 값들을 설정하세요:
```
봇토큰=YOUR_DISCORD_BOT_TOKEN
특정유저=USER_ID1,USER_ID2  # TTS 기능을 사용할 사용자 ID (쉼표로 구분)
특정채널=CHANNEL_ID1,CHANNEL_ID2  # TTS 기능을 사용할 채널 ID (쉼표로 구분)
```

### 3. 봇 실행
```bash
# 방법 1: 가상환경 활성화 후 실행
source venv/bin/activate
python src/osage_chan/main.py

# 방법 2: 직접 가상환경 Python 사용 (권장)
/home/dev/Osage_chan_discord_bot/.venv/bin/python src/osage_chan/main.py

# 방법 3: run.sh 스크립트 사용
chmod +x run.sh
./run.sh
```

### 4. 봇 중지
터미널에서 `Ctrl+C`를 눌러 봇을 중지할 수 있습니다.

---

## 주요 기능

- **TTS 기능**  
  설정된 사용자가 특정 채널에서 메시지를 입력하면, Edge TTS를 사용하여 음성으로 변환 후 재생합니다.
  - 한글 자모 분해 및 발음 변환 지원
  - URL 링크는 "링크를 보냄"으로 읽어줍니다

- **음악 재생**  
  YouTube URL을 다운로드하여 음성 채널에서 재생합니다.

### 명령어
- `!p [URL]`: YouTube URL 재생 또는 재생목록에 추가
- `!s`: 현재 재생 중인 노래 중지
- `!c`: 재생목록 전체 삭제
- `!r`: 재생목록에서 첫 번째 곡 삭제

---

## 필요한 패키지

- discord.py: 디스코드 봇 라이브러리
- PyNaCl: 음성 연결용
- edge-tts: Microsoft Edge TTS
- yt-dlp: YouTube 다운로더
- python-dotenv: 환경변수 로드

---


## 폴더 구조

- `/home/dev/osage_chan_github/main.py`: 봇의 주요 소스코드 파일.
- `/home/dev/osage_chan_github/README.md`: 이 파일.
- `voice/`: TTS 및 음악 재생에 사용되는 임시 음성 파일들이 저장되는 폴더.

---

## 참고

- 보다 많은 설정과 커스터마이징 옵션은 코드 내 주석을 참고해 주세요.
- 오류 발생 시, 터미널의 출력 로그를 확인하거나 Discord 개발자 포털의 가이드 문서를 참조하시기 바랍니다.

Happy Coding!