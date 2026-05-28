import nextcord
from nextcord.ext import commands
import os
import yt_dlp
import requests
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- ระบบเปิดพอร์ต 24 ชม. ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running 24/7!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

load_dotenv()
intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

ydl_opts = {
    'format': 'bestaudio/best',
    'cookiefile': 'cookies.txt', 
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'webm', 'preferredquality': '192'}],
}
ffmpeg_options = {'options': '-vn -loglevel quiet'}

# --- คำสั่งทั้งหมด ---

@bot.slash_command(name="weather", description="เช็กสภาพอากาศ")
async def weather(interaction: nextcord.Interaction, city: str):
    # ใส่ API Key ให้เรียบร้อยแล้วครับ
    api_key = "984cc187c35afb6f1b44d39de7fb191e" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=th"
    try:
        await interaction.response.defer() 
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return await interaction.followup.send("❌ ไม่พบเมืองนี้ครับ โปรดตรวจสอบชื่อเมืองอีกครั้ง")
        
        city_name = response["name"]
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        await interaction.followup.send(f"🌤️ อากาศที่ {city_name}: {desc} อุณหภูมิ {temp}°C")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.slash_command(name="play", description="เล่นเพลงจาก YouTube")
async def play(interaction: nextcord.Interaction, url: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ ต้องอยู่ในห้องเสียงก่อนครับ")
    
    await interaction.response.defer()
    
    try:
        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect()
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info.get('url')
            source = await nextcord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
            
            if interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.stop()
            
            interaction.guild.voice_client.play(source)
            await interaction.followup.send(f"🎵 กำลังเล่น: {info['title']}")
    except Exception as e:
        await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

bot.run(os.getenv('DISCORD_TOKEN'))
