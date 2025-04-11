import discord
from discord.ext import commands
import os
import subprocess

# Configure bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Constants
SPECIFIC_USER_ID = 123456789012345678  # Replace with the authorized user's Discord ID
TTS_OUTPUT_FILE = "tts.wav"
GGUF_MODEL_PATH = "/home/dev/mia_chan/model/Llama-OuteTTS-1.0-1B-Q4_K_M.gguf"  # Replace with your .gguf file name
VOICE_FOLDER = "/home/dev/mia_chan/voice/"  # Folder for voice sample files
SPECIFIC_CHANNEL_ID = 987654321098765432  # Replace with the target text channel's ID

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    """Automatically generate TTS when a specific user sends a message in a specific channel."""
    if message.author.id == SPECIFIC_USER_ID and message.channel.id == SPECIFIC_CHANNEL_ID:
        if message.guild.voice_client:  # Check if the bot is connected to a voice channel
            command = [
                "ollama", "generate",
                "--model", GGUF_MODEL_PATH,
                "--input", message.content,
                "--output", TTS_OUTPUT_FILE
            ]

            try:
                # Generate TTS audio
                subprocess.run(command, check=True)
                # Play the generated audio
                message.guild.voice_client.play(
                    discord.FFmpegPCMAudio(TTS_OUTPUT_FILE),
                    after=lambda e: os.remove(TTS_OUTPUT_FILE) if os.path.exists(TTS_OUTPUT_FILE) else None
                )
            except subprocess.CalledProcessError as e:
                await message.channel.send("TTS 오디오 생성에 실패했습니다.")
                print(f"오류: {e}")
            except Exception as e:
                await message.channel.send("예기치 못한 오류가 발생했습니다.")
                print(f"예기치 못한 오류: {e}")
        else:
            await message.channel.send("봇이 음성 채널에 연결되어 있지 않습니다.")
    
    # Ensure other commands still work
    await bot.process_commands(message)

@bot.command()
async def join(ctx):
    """Command to make the bot join the user's voice channel."""
    if ctx.author.id != SPECIFIC_USER_ID:
        await ctx.send("You are not authorized to use this command.")
        return

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

@bot.command()
async def leave(ctx):
    """Command to make the bot leave the voice channel."""
    if ctx.author.id != SPECIFIC_USER_ID:
        await ctx.send("You are not authorized to use this command.")
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def tts(ctx, text: str, voice_sample: str = None):
    """음성 클론 옵션을 사용하여 TTS 오디오를 생성하고 음성 채널에서 재생하는 명령어."""
    if ctx.author.id != SPECIFIC_USER_ID:
        await ctx.send("이 명령어를 사용할 권한이 없습니다.")
        return

    if ctx.voice_client:
        command = [
            "ollama", "generate",
            "--model", GGUF_MODEL_PATH,
            "--input", text,
            "--output", TTS_OUTPUT_FILE
        ]

        # 음성 샘플이 제공되었을 경우 추가
        if voice_sample:
            voice_sample_path = os.path.join(VOICE_FOLDER, voice_sample)
            if os.path.exists(voice_sample_path):
                command.extend(["--voice-sample", voice_sample_path])
            else:
                await ctx.send("지정된 음성 샘플 파일이 존재하지 않습니다.")
                return

        try:
            # .gguf 모델과 선택적 음성 샘플을 사용하여 TTS 오디오 생성
            subprocess.run(command, check=True)
            # 생성된 오디오 재생
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(TTS_OUTPUT_FILE),
                after=lambda e: os.remove(TTS_OUTPUT_FILE) if os.path.exists(TTS_OUTPUT_FILE) else None
            )
        except subprocess.CalledProcessError as e:
            await ctx.send("TTS 오디오 생성에 실패했습니다.")
            print(f"오류: {e}")
        except Exception as e:
            await ctx.send("예기치 못한 오류가 발생했습니다.")
            print(f"예기치 못한 오류: {e}")
    else:
        await ctx.send("음성 채널에 있어야 TTS를 재생할 수 있습니다.")

# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot.run("YOUR_BOT_TOKEN")
