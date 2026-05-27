import nextcord
from nextcord.ext import commands
import base64, codecs
import os
import urllib.request
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# ==================================================
# 🌐 โซนระบบเปิดพอร์ต (Keep Alive) หลอกระบบ Railway ให้บอทออนไลน์ 24 ชม.
# ==================================================
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==================================================
# 🤖 โซนตั้งค่าตัวบอท Discord (Nextcord)
# ==================================================
load_dotenv()

intents = nextcord.Intents.all()
intents.message_content = True  
intents.voice_states = True     

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# 📍 โค้ดส่วนไอดีเซิร์ฟเวอร์ของคุณ
BotSever1 = 1204647300870311986 
BotSever2 = 1468565605836918846

# 📍 โค้ดส่วน Event: เมื่อบอทออนไลน์สำเร็จ (เซ็ตสถานะปุ่มม่วง)
@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Streaming(name="Phakaphop", url="https://www.twitch.tv/..."))
    print('Bot is ready.')

# 📍 โค้ดส่วน Event: ตรวจจับคนเปิดสตรีมในห้องเสียง
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.self_stream:
        # บรรทัดนี้จะแจ้งเตือนในหน้า Log ของ Railway เวลาที่มีคนเริ่มเปิดสตรีมจอในห้องเสียงครับ
        print(f'{member.name} is in {after.channel.name}')

# ==================================================
# 🚀 โซนคำสั่งสำหรับทดสอบพิมพ์คุยใน Discord
# ==================================================
@bot.command()
async def ping(ctx):
    await ctx.send("บอทออนไลน์และพร้อมรับคำสั่งแล้วครับ! 🚀")

@bot.command()
async def hello(ctx):
    await ctx.send(f"สวัสดีครับคุณ {ctx.author.name} ! 😊")

# ==================================================
# 🛑 สั่งรันระบบทั้งหมด
# ==================================================
keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
