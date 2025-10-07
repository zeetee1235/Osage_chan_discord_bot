import discord
from discord.ext import commands
import edge_tts
import asyncio
import subprocess
import yt_dlp as youtube_dl  # 기존의 'import youtube_dl' 대신 yt-dlp 사용
import os  # 추가: 폴더 생성을 위해 os 모듈 import
from dotenv import load_dotenv
import uuid  # 고유 파일 이름 생성을 위해 추가
import json  # 추가: json 모듈 import
import logging  # 로깅 추가
from osage_chan.hangul import spell_any_korean

# 로깅 설정 - 에러 로그만 출력하도록 설정
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# .env 환경변수 로드
load_dotenv()
ALLOWED_USER_IDS = [int(uid) for uid in os.getenv("특정유저", "").split(",") if uid]
TTS_OUTPUT_FILE = "./voice/tts.wav"
SPECIFIC_CHANNEL_IDS = [int(cid) for cid in os.getenv("특정채널", "").split(",") if cid]
BOT_TOKEN = os.getenv("봇토큰")

# 추가: 봇 인텐트 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

# youtube_dl 옵션 상수 추가 - 포맷 호환성 개선
YDL_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best[height<=720]/best',  # 더 유연한 포맷 선택
    'noplaylist': True,
    'extract_flat': False,
    'writethumbnail': False,
    'writeinfojson': False,
    'writesubtitles': False,
    'writeautomaticsub': False,
    'ignoreerrors': False,
    'no_warnings': True,
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(id)s.%(ext)s',
    'retries': 3,
    'fragment_retries': 3,
    'socket_timeout': 60,
    'prefer_ffmpeg': True,  # ffmpeg 우선 사용
}
FFMPEG_OPTIONS = {'options': '-vn -threads 2'}  # 멀티스레딩 활성화

# 전역 재생목록(큐): 하나의 파일만 사용하므로 글로벌 리스트로 관리
queue = []

async def tts(message):
    try:
        # "voice" 폴더 존재 여부 확인 및 없으면 생성
        os.makedirs("voice", exist_ok=True)
        import re
        url_pattern = re.compile(r"https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+")
        msg = message.content.strip()
        if url_pattern.fullmatch(msg):
            text = "링크를 보냄"
        else:
            # 한글 자모 및 일반 텍스트를 발음 변환
            text = spell_any_korean(msg, style="casual")
        voice = "ko-KR-SunHiNeural"
        mp3_file = "voice/output.mp3"
        wav_file = "voice/output.wav"

        communicate = edge_tts.Communicate(text, voice, pitch="+10Hz", rate="+20%")
        await communicate.save(mp3_file)
        
        # ffmpeg를 이용하여 mp3 -> wav로 변환
        try:
            subprocess.run(["ffmpeg", "-y", "-i", mp3_file, wav_file], 
                         check=True, capture_output=True, timeout=30)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error(f"ffmpeg 변환 실패: {e}")
            return
        
        print(f"음성 파일이 저장되었습니다: {wav_file}")
    except Exception as e:
        logger.error(f"TTS 처리 중 오류 발생: {e}")
        return

# TTS 초기 실행 호출을 주석 처리
# asyncio.run(main())

# 봇 초기화
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_voice_state_update(member, before, after):
    try:
        # 특정 사용자만 처리
        if member.id not in ALLOWED_USER_IDS:
            return
        # 사용자가 음성 채널에 들어갔을 때 및 이동할 때
        if after.channel:
            voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
            if voice_client is None:
                await after.channel.connect()
            else:
                await voice_client.move_to(after.channel)
        # 사용자가 음성 채널에서 나갔을 때
        else:
            voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
            if voice_client:
                await voice_client.disconnect()
    except Exception as e:
        logger.error(f"음성 상태 업데이트 중 오류: {e}")

@bot.event
async def on_message(message):
    try:
        # 봇 메시지는 무시
        if message.author.bot:
            return
        # 커맨드("!") 메시지면 TTS 처리를 건너뜁니다.
        if message.content.startswith("!"):
            await bot.process_commands(message)
            return
        if message.author.id in ALLOWED_USER_IDS and message.channel.id in SPECIFIC_CHANNEL_IDS:
            await tts(message)
            # 메시지 작성자의 음성 채널 확인 및 봇 이동 처리
            if message.author.voice and message.author.voice.channel:
                voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)
                if voice_client is None:
                    voice_client = await message.author.voice.channel.connect()
                elif voice_client.channel != message.author.voice.channel:
                    await voice_client.move_to(message.author.voice.channel)
            else:
                # 음성 채널이 없으면 재생하지 않음
                return
            # 저장된 음성 파일 재생 (이미 ffmpeg로 변환된 wav 파일)
            try:
                if os.path.exists("voice/output.wav"):
                    source = discord.FFmpegPCMAudio("voice/output.wav")
                    if voice_client and not voice_client.is_playing():
                        voice_client.play(source)
            except Exception as e:
                logger.error(f"음성 재생 중 오류: {e}")
        # 다른 명령어도 처리
        await bot.process_commands(message)
    except Exception as e:
        logger.error(f"메시지 처리 중 오류: {e}")

async def download_and_play(voice_client, url: str, ctx=None):
    """
    URL을 다운로드 후, mp3 -> wav 변환하여 재생.
    각 곡마다 고유한 파일 이름을 생성하여 덮어쓰임을 방지.
    """
    unique_id = str(uuid.uuid4())  # 고유 ID 생성
    mp3_path = f"voice/music_{unique_id}.mp3"
    wav_path = f"voice/music_{unique_id}.wav"
    
    # 다운로드 진행 상황 알림
    if ctx:
        status_msg = await ctx.send("🎵 음악을 다운로드하고 있습니다...")
    
    try:
        # 여러 포맷 옵션으로 시도
        format_options = [
            'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
            'best[height<=720]/best[height<=480]/best',
            'worstaudio/worst'  # 마지막 수단
        ]
        
        downloaded = False
        for format_opt in format_options:
            try:
                ydl_download_opts = {
                    **YDL_OPTIONS, 
                    "outtmpl": mp3_path,
                    "format": format_opt
                }
                
                with youtube_dl.YoutubeDL(ydl_download_opts) as ydl:
                    await asyncio.get_event_loop().run_in_executor(
                        None, lambda: ydl.download([url])
                    )
                downloaded = True
                break
            except Exception as e:
                logger.error(f"포맷 {format_opt} 다운로드 실패: {e}")
                continue
        
        if not downloaded:
            if ctx:
                await status_msg.edit(content="❌ 사용 가능한 포맷을 찾을 수 없습니다.")
            return
        
        if ctx:
            await status_msg.edit(content="🔄 음성 파일을 변환하고 있습니다...")
        
        # 다운로드된 파일 확인 및 이름 변경
        downloaded_files = [f for f in os.listdir("voice") if f.startswith(f"music_{unique_id}")]
        if not downloaded_files:
            if ctx:
                await status_msg.edit(content="❌ 다운로드된 파일을 찾을 수 없습니다.")
            return
        
        # 첫 번째 다운로드된 파일을 사용
        actual_file = f"voice/{downloaded_files[0]}"
        
        # ffmpeg 변환 (비동기, 타임아웃 제거)
        try:
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-y', '-i', actual_file, 
                '-acodec', 'pcm_s16le', '-ac', '2', '-ar', '48000',
                wav_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"ffmpeg 변환 실패: {stderr.decode()}")
                raise Exception("ffmpeg 변환 실패")
                
        except Exception as e:
            logger.error(f"ffmpeg 변환 오류: {e}")
            if ctx:
                await status_msg.edit(content="❌ 변환 중 오류가 발생했습니다.")
            return
            
        source = discord.FFmpegPCMAudio(wav_path, **FFMPEG_OPTIONS)
        
        if ctx:
            await status_msg.edit(content="✅ 음악을 재생합니다!")
        
    except Exception as e:
        logger.error(f"다운로드 또는 변환 중 오류: {e}")
        if ctx:
            await status_msg.edit(content="❌ 다운로드 중 오류가 발생했습니다.")
        # 파일 삭제 안전 처리
        cleanup_files = [mp3_path, wav_path] + [f"voice/{f}" for f in os.listdir("voice") if f.startswith(f"music_{unique_id}")]
        for f in cleanup_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass
        return
        
    def after_playing(err):
        if err:
            logger.error(f"재생 중 오류: {err}")
        # 파일 삭제 안전 처리
        cleanup_files = [mp3_path, wav_path] + [f"voice/{f}" for f in os.listdir("voice") if f.startswith(f"music_{unique_id}")]
        for f in cleanup_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass
        # 다음 곡 재생
        try:
            coro = play_next(voice_client)
            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            fut.result(timeout=5)
        except Exception as exc:
            logger.error(f"다음 곡 재생 중 오류: {exc}")
            
    try:
        if voice_client and voice_client.is_connected():
            voice_client.play(source, after=after_playing)
        else:
            logger.error("음성 클라이언트가 연결되지 않음")
            after_playing(None)
    except Exception as e:
        logger.error(f"오디오 재생 중 오류: {e}")
        after_playing(None)

async def play_next(voice_client):
    """
    재생 종료 후, 큐에서 다음 곡을 재생.
    """
    try:
        if queue and voice_client and voice_client.is_connected():
            next_url = queue.pop(0)
            await download_and_play(voice_client, next_url)  # ctx 없이 호출
        else:
            print("재생목록이 비었습니다.")
    except Exception as e:
        logger.error(f"다음 곡 재생 중 오류: {e}")

@bot.command(name='p')
async def play(ctx, url: str):
    """
    URL을 재생하거나 재생목록에 추가.
    """
    try:
        if ctx.author.id not in ALLOWED_USER_IDS:
            return
        if ctx.author.voice and ctx.author.voice.channel:
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            if voice_client is None:
                voice_client = await ctx.author.voice.channel.connect()
            elif voice_client.channel != ctx.author.voice.channel:
                await voice_client.move_to(ctx.author.voice.channel)
        else:
            await ctx.send("먼저 음성 채널에 접속해주세요.")
            return
        # 큐에 추가하거나 즉시 재생
        if voice_client.is_playing() or queue:
            queue.append(url)
            await ctx.send("노래를 재생목록에 추가했습니다.")
        else:
            await download_and_play(voice_client, url, ctx)  # ctx 전달
    except Exception as e:
        logger.error(f"재생 명령 처리 중 오류: {e}")
        await ctx.send("음악 재생 중 오류가 발생했습니다.")

@bot.command(name='c')
async def clear_queue(ctx):
    """
    재생목록의 모든 곡을 삭제합니다.
    """
    if ctx.author.id not in ALLOWED_USER_IDS:
        return
    global queue
    queue.clear()
    await ctx.send("재생목록이 모두 삭제되었습니다.")

@bot.command(name='r')
async def remove_first(ctx):
    """
    재생목록의 가장 앞에 있는 곡을 삭제합니다.
    """
    if ctx.author.id not in ALLOWED_USER_IDS:
        return
    global queue
    if queue:
        removed_song = queue.pop(0)
        await ctx.send(f"재생목록에서 가장 앞에 있는 곡이 삭제되었습니다: {removed_song}")
    else:
        await ctx.send("재생목록이 비어 있습니다.")

@bot.command(name='s')
async def stop(ctx):
    """
    현재 재생 중인 노래를 중지합니다.
    """
    try:
        if ctx.author.id not in ALLOWED_USER_IDS:
            return
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("현재 재생 중인 노래를 중지했습니다.")
        else:
            await ctx.send("현재 재생 중인 노래가 없습니다.")
    except Exception as e:
        logger.error(f"정지 명령 처리 중 오류: {e}")
        await ctx.send("노래 정지 중 오류가 발생했습니다.")

# 봇 연결 끊김 이벤트 처리
@bot.event
async def on_disconnect():
    logger.warning("봇이 Discord에서 연결 해제됨")

# 에러 핸들러 추가
@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"이벤트 {event}에서 오류 발생", exc_info=True)

# 봇 토큰으로 실행
try:
    bot.run(BOT_TOKEN)
except Exception as e:
    logger.error(f"봇 실행 중 치명적 오류: {e}")
