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
    # ดึงค่าพอร์ตที่ Railway จ่ายมาให้ ถ้าไม่มีจะใช้พอร์ต 8080 เป็นค่าเริ่มต้น
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==================================================
# 🤖 โซนตั้งค่าตัวบอท Discord (Nextcord)
# ==================================================
# โหลดค่าตัวแปรจากระบบ (Environment Variables หรือ .env)
load_dotenv()

# เปิดสิทธิ์การเข้าถึงทั้งหมดเพื่อให้บอทอ่านข้อความและเช็กห้องเสียงได้
intents = nextcord.Intents.all()
intents.message_content = True  
intents.voice_states = True     

# สร้างตัวแปรบอท (ใช้เครื่องหมาย ! นำหน้าคำสั่ง)
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ไอดีเซิร์ฟเวอร์ของคุณ
BotSever1 = 1204647300870311986 
BotSever2 = 1468565605836918846

# Event: เมื่อบอทออนไลน์สำเร็จ
@bot.event
async def on_ready():
    # ตั้งค่าสถานะบอทให้ขึ้นว่า "กำลังสตรีม Phakaphop" (ปุ่มสีม่วง)
    await bot.change_presence(activity=nextcord.Streaming(name="Phakaphop", url="https://www.twitch.tv/..."))
    print('Bot is ready.')

# Event: เมื่อมีคนเข้า-ออก หรือเปิดไมค์ในห้องเสียง
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.self_stream:
        print(f'{member.name} is in {after.channel.name}')

# ==================================================
# 🚀 โซนคำสั่ง (Commands) สำหรับพิมพ์คุยใน Discord
# ==================================================

# 1. คำสั่ง !ping (เช็กสถานะบอท)
@bot.command()
async def ping(ctx):
    await ctx.send("บอทออนไลน์และพร้อมรับคำสั่งแล้วครับ! 🚀")

# 2. คำสั่ง !hello (ทักทายผู้ใช้)
@bot.command()
async def hello(ctx):
    await ctx.send(f"สวัสดีครับคุณ {ctx.author.name} มีอะไรให้ผมรับใช้ไหมครับ? 😊")

# ==================================================
# 🛑 สั่งรันระบบทั้งหมดล่างสุดของไฟล์
# ==================================================
# เรียกเปิดพอร์ตเว็บหลอก Railway
keep_alive()

# ดึง Token จาก Railway Variables แล้วสั่งให้บอทเริ่มทำงาน
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
