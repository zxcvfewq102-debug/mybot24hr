import nextcord
from nextcord.ext import commands
import os
import yt_dlp
import requests
import openai
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
# ดึงคีย์จากตัวแปรสภาพแวดล้อม (ปลอดภัยที่สุด)
openai.api_key = os.getenv("OPENAI_API_KEY")

intents = nextcord.Intents.all()
intents.message_content = True
bot = commands.Bot(intents=intents)

# ระบบคิวเพลง
queues = {}
ydl_opts = {'format': 'bestaudio/best', 'cookiefile': 'cookies.txt', 'noplaylist': True}
ffmpeg_options = {'options': '-vn -loglevel quiet'}

# --- ระบบ AI Chat ---
async def get_ai_response(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ขอโทษครับ ระบบ AI มีปัญหา: {str(e)}"

# --- ฟังก์ชันเล่นเพลงถัดไป ---
async def play_next(interaction):
    guild_id = interaction.guild.id
    if queues.get(guild_id):
        video = queues[guild_id].pop(0)
        source = await nextcord.FFmpegOpusAudio.from_probe(video['url'], **ffmpeg_options)
        interaction.guild.voice_client.play(source, after=lambda e: bot.loop.create_task(play_next(interaction)))
        await interaction.channel.send(f"🎵 กำลังเล่น: {video['title']}")
    else:
        await interaction.channel.send("✅ เล่นคิวเพลงจนหมดแล้วครับ")

# --- คำสั่ง ---
@bot.slash_command(name="chat", description="คุยกับบอท AI")
async def chat(interaction: nextcord.Interaction, message: str):
    await interaction.response.defer()
    response = await get_ai_response(message)
    await interaction.followup.send(f"🤖 **AI ตอบว่า:**\n{response}")

@bot.slash_command(name="weather", description="เช็กสภาพอากาศ")
async def weather(interaction: nextcord.Interaction, city: str):
    api_key = "984cc187c35afb6f1b44d39de7fb191e" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=th"
    try:
        await interaction.response.defer()
        response = requests.get(url).json()
        if response.get("cod") != 200: return await interaction.followup.send("❌ ไม่พบเมืองนี้ครับ")
        await interaction.followup.send(f"🌤️ อากาศที่ {response['name']}: {response['weather'][0]['description']} อุณหภูมิ {response['main']['temp']}°C")
    except Exception as e: await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.slash_command(name="play", description="ค้นหาและเล่นเพลง")
async def play(interaction: nextcord.Interaction, search: str):
    if not interaction.user.voice: return await interaction.response.send_message("❌ ต้องเข้าห้องเสียงก่อน")
    await interaction.response.defer()
    if interaction.guild.id not in queues: queues[interaction.guild.id] = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)
        video = info['entries'][0] if 'entries' in info else info
        queues[interaction.guild.id].append(video)
        await interaction.followup.send(f"➕ เพิ่มเข้าคิว: {video['title']}")
        if not interaction.guild.voice_client: await interaction.user.voice.channel.connect()
        if not interaction.guild.voice_client.is_playing(): await play_next(interaction)

@bot.slash_command(name="skip", description="ข้ามเพลง")
async def skip(interaction: nextcord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ ข้ามเพลงเรียบร้อย!")
    else: await interaction.response.send_message("❌ ไม่ได้เล่นเพลงอยู่ครับ")

bot.run(os.getenv('DISCORD_TOKEN'))
