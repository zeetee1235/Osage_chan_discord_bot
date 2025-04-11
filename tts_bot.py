import discord
from discord.ext import commands
import os
import subprocess  # For calling external commands like `ollama`

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def tts(ctx, *, text: str):
    if ctx.voice_client:
        # Use ollama to generate TTS audio from text
        output_file = "tts.wav"
        command = ["ollama", "generate", "--input", text, "--output", output_file]
        try:
            subprocess.run(command, check=True)  # Run the ollama command
            ctx.voice_client.play(discord.FFmpegPCMAudio(output_file), after=lambda e: os.remove(output_file))
        except subprocess.CalledProcessError as e:
            await ctx.send("Failed to generate TTS audio.")
            print(f"Error: {e}")
    else:
        await ctx.send("I need to be in a voice channel to play TTS.")

# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot.run("YOUR_BOT_TOKEN")
