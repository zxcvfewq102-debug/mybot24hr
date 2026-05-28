import nextcord
from nextcord.ext import commands
import os
import yt_dlp
import requests
import random
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- ระบบเปิดพอร์ต 24 ชม. ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

load_dotenv()
intents = nextcord.Intents.all()
intents.message_content = True
bot = commands.Bot(intents=intents)

# ตั้งค่า yt-dlp ให้ดึงคุกกี้จากไฟล์ cookies.txt
ydl_opts = {
    'format': 'bestaudio/best',
    'cookiefile': 'cookies.txt', 
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}
ffmpeg_options = {'options': '-vn -loglevel quiet'}

# --- ระบบตอบโต้แชท ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if "สวัสดี" in message.content: await message.channel.send(f"สวัสดีครับคุณ {message.author.mention} มีอะไรให้ผมรับใช้ไหมครับ?")
    await bot.process_commands(message)

# --- Slash Commands ---
@bot.slash_command(name="ping", description="เช็กความหน่วงบอท")
async def ping(interaction: nextcord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 ({round(bot.latency * 1000)}ms)")

@bot.slash_command(name="play", description="เล่นเพลงจาก YouTube")
async def play(interaction: nextcord.Interaction, search: str):
    if not interaction.user.voice: return await interaction.response.send_message("❌ ต้องเข้าห้องเสียงก่อนครับ")
    await interaction.response.defer()
    try:
        if not interaction.guild.voice_client: await interaction.user.voice.channel.connect()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            video = info['entries'][0] if 'entries' in info else info
            source = await nextcord.FFmpegOpusAudio.from_probe(video['url'], **ffmpeg_options)
            if interaction.guild.voice_client.is_playing(): interaction.guild.voice_client.stop()
            interaction.guild.voice_client.play(source)
            await interaction.followup.send(f"🎵 กำลังเล่น: {video.get('title')}")
    except Exception as e: await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

@bot.slash_command(name="leave", description="บอทออกจากห้อง")
async def leave(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("📤 ออกจากห้องแล้วครับ")
    else: await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

bot.run(os.getenv('DISCORD_TOKEN'))
