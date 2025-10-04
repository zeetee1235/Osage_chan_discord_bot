#!/bin/bash
# Osage_chan_discord_bot 프로젝트 세팅 스크립트

set -e

# 1. Python 가상환경 생성
echo "[1/3] 가상환경 생성 중..."
python3 -m venv venv

echo "[2/3] 가상환경 활성화 안내"
echo "  source venv/bin/activate"

echo "[3/3] requirements.txt로 패키지 설치 중..."
source venv/bin/activate
# uv가 설치되어 있지 않으면 설치
if ! command -v uv &> /dev/null; then
	echo "uv가 설치되어 있지 않습니다. 설치를 진행합니다..."
	pip install uv
fi
uv pip install -r requirements.txt

echo "voice 폴더가 없으면 생성합니다."
mkdir -p voice

echo "\n설정 완료! 가상환경을 활성화하려면 아래 명령을 입력하세요:"
echo "  source venv/bin/activate"
