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
intents.message_content = True # สำคัญ: ต้องเปิดให้บอทอ่านข้อความได้
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

# --- ระบบตอบกลับอัตโนมัติ (แก้ไขให้ถูกต้อง) ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # คำทักทาย
    if "สวัสดี" in message.content:
        await message.channel.send(f"สวัสดีครับคุณ {message.author.mention} มีอะไรให้ผมรับใช้ไหมครับ?")
    
    # คำสั่งโปร
    if "ขอโปรหน่อย" in message.content:
        await message.channel.send(f"นี่ครับโปรของคุณ {message.author.mention} 🎁")
        
    await bot.process_commands(message)

# --- Slash Commands ---
@bot.slash_command(name="hello", description="ทักทายบอท")
async def hello(interaction: nextcord.Interaction):
    await interaction.response.send_message(f"สวัสดีครับ {interaction.user.mention}! ผมพร้อมใช้งานแล้วครับ 🤖")

@bot.slash_command(name="weather", description="เช็กสภาพอากาศ")
async def weather(interaction: nextcord.Interaction, city: str):
    api_key = "984cc187c35afb6f1b44d39de7fb191e" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=th"
    try:
        await interaction.response.defer()
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return await interaction.followup.send("❌ ไม่พบเมืองนี้ครับ")
        city_name = response["name"]
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        await interaction.followup.send(f"🌤️ อากาศที่ {city_name}: {desc} อุณหภูมิ {temp}°C")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.slash_command(name="play", description="เล่นเพลงจากชื่อเพลงหรือลิงก์")
async def play(interaction: nextcord.Interaction, search: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ ต้องอยู่ในห้องเสียงก่อนครับ")
    await interaction.response.defer()
    try:
        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
            
            url2 = video.get('url')
            title = video.get('title')
            source = await nextcord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
            
            if interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.stop()
            
            interaction.guild.voice_client.play(source)
            await interaction.followup.send(f"🎵 กำลังเล่น: {title}")
    except Exception as e:
        await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

@bot.slash_command(name="stop", description="หยุดเพลง")
async def stop(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏹️ หยุดเล่นเพลงแล้วครับ")
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

@bot.slash_command(name="leave", description="ให้บอทออกจากห้อง")
async def leave(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("📤 ออกจากห้องแล้วครับ")
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

bot.run(os.getenv('DISCORD_TOKEN'))
