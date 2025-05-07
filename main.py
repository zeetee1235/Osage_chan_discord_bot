import discord
from discord.ext import commands
import edge_tts
import asyncio
import subprocess
import yt_dlp as youtube_dl  # 기존의 'import youtube_dl' 대신 yt-dlp 사용
import os  # 추가: 폴더 생성을 위해 os 모듈 import
import uuid  # 고유 파일 이름 생성을 위해 추가

# 봇 인텐트 설정
intents = discord.Intents.default()
intents.messages = True  # "서버 멤버 인텐트"를 개발자 포털에서 활성화해야 함
intents.message_content = True  # "메시지 내용 인텐트"를 개발자 포털에서 활성화해야 함
intents.guilds = True
intents.voice_states = True

# 상수
ALLOWED_USER_IDS = []  # 기존 SPECIFIC_USER_ID 대신 리스트 사용
TTS_OUTPUT_FILE = "./voice/tts.wav"
SPECIFIC_CHANNEL_ID = None #특정 채널 ID
BOT_TOKEN = None

# youtube_dl 옵션 상수 추가
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
FFMPEG_OPTIONS = {'options': '-vn'}

# 전역 재생목록(큐): 하나의 파일만 사용하므로 글로벌 리스트로 관리
queue = []

async def tts(message):
    # "voice" 폴더 존재 여부 확인 및 없으면 생성
    os.makedirs("voice", exist_ok=True)
    text = message.content
    voice = "ko-KR-SunHiNeural"
    mp3_file = "voice/output.mp3"
    wav_file = "voice/output.wav"

    communicate = edge_tts.Communicate(text, voice, pitch="+10Hz", rate="+20%")
    await communicate.save(mp3_file)
    
    # ffmpeg를 이용하여 mp3 -> wav로 변환
    subprocess.run(["ffmpeg", "-y", "-i", mp3_file, wav_file])
    
    print(f"음성 파일이 저장되었습니다: {wav_file}")

# TTS 초기 실행 호출을 주석 처리
# asyncio.run(main())

# 봇 초기화
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_voice_state_update(member, before, after):
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

@bot.event
async def on_message(message):
    # 봇 메시지는 무시
    if message.author.bot:
        return
    # 커맨드("!") 메시지면 TTS 처리를 건너뜁니다.
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return
    if message.author.id in ALLOWED_USER_IDS and message.channel.id == SPECIFIC_CHANNEL_ID:
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
        source = discord.FFmpegPCMAudio("voice/output.wav")
        if not voice_client.is_playing():
            voice_client.play(source)
    # 다른 명령어도 처리
    await bot.process_commands(message)

async def download_and_play(voice_client, url: str):
    """
    URL을 다운로드 후, mp3 -> wav 변환하여 재생.
    각 곡마다 고유한 파일 이름을 생성하여 덮어쓰임을 방지.
    """
    unique_id = str(uuid.uuid4())  # 고유 ID 생성
    mp3_path = f"voice/music_{unique_id}.mp3"
    wav_path = f"voice/music_{unique_id}.wav"
    ydl_opts = {**YDL_OPTIONS, "outtmpl": mp3_path}
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error downloading: {e}")
        return
    subprocess.run(["ffmpeg", "-y", "-i", mp3_path, wav_path])
    source = discord.FFmpegPCMAudio(wav_path)
    def after_playing(err):
        # 파일 삭제
        os.remove(mp3_path)
        os.remove(wav_path)
        coro = play_next(voice_client)
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except Exception as exc:
            print(f"Error in play_next: {exc}")
    voice_client.play(source, after=after_playing)

async def play_next(voice_client):
    """
    재생 종료 후, 큐에서 다음 곡을 재생.
    """
    if queue:
        next_url = queue.pop(0)
        await download_and_play(voice_client, next_url)
    else:
        print("재생목록이 비었습니다.")

@bot.command(name='p')
async def play(ctx, url: str):
    """
    URL을 재생하거나 재생목록에 추가.
    """
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
        await download_and_play(voice_client, url)
        await ctx.send("노래 재생을 시작합니다.")

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
    if ctx.author.id not in ALLOWED_USER_IDS:
        return
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("현재 재생 중인 노래를 중지했습니다.")
    else:
        await ctx.send("현재 재생 중인 노래가 없습니다.")

# 봇 토큰으로 실행
bot.run(BOT_TOKEN)
