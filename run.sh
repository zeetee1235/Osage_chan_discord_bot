#!/bin/bash
# Osage_chan_discord_bot 실행 스크립트

set -e

# uv 환경에서 main.py 실행
echo "uv 환경에서 main.py를 실행합니다..."
uv run python src/osage_chan/main.py
