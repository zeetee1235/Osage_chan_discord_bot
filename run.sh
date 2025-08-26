#!/bin/bash
# Osage_chan_discord_bot 실행 스크립트

set -e

# uv 환경에서 main.py 실행
echo "uv 환경에서 main.py를 실행합니다..."
if [ -d ".uv" ]; then
	UV_PATH="./.uv/bin/uv"
elif command -v uv &> /dev/null; then
	UV_PATH="uv"
else
	echo "uv가 설치되어 있지 않습니다. 로컬 설치를 진행합니다..."
	python3 -m venv .uv
	./.uv/bin/pip install --upgrade pip
	./.uv/bin/pip install uv
	UV_PATH="./.uv/bin/uv"
fi
$UV_PATH run python src/osage_chan/main.py
