import nextcord
from nextcord.ext import commands
import base64, codecs
import os
import urllib.request
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# 🌐 โซนระบบเปิดพอร์ตหลอก Railway ให้บอทออนไลน์ 24 ชั่วโมง
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    # ดึงค่าพอร์ตที่ Railway จ่ายมาให้ ถ้าไม่มีจะใช้พอร์ต 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()
# --------------------------------------------------

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ตั้งค่าสิทธิ์การเข้าถึงให้บอท
intents = nextcord.Intents.all()
intents.message_content = True  
intents.voice_states = True     

# สร้างตัวแปรบอทและส่งค่า intents เข้าไปด้วย เพื่อให้บอทรับคำสั่งได้
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

BotSever1 = 1204647300870311986 
BotSever2 = 1468565605836918846

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Streaming(name="Phakaphop", url="https://www.twitch.tv/..."))
    print('Bot is ready.')

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.self_stream:
        print(f'{member.name} is in {after.channel.name}')

# 🚀 โซนคำสั่งทดสอบ (พิมพ์ !ping ในดิสคอร์ดเพื่อลองเรียกบอท)
@bot.command()
async def ping(ctx):
    await ctx.send("บอทออนไลน์และพร้อมรับคำสั่งแล้วครับ! 🚀")


# 🛑 เรียกใช้งานระบบเปิดพอร์ต ก่อนสั่งรันบอทล่างสุด
keep_alive()

# ดึง Token จากระบบของ Railway และสั่งรันบอททำงาน
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
