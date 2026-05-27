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

# ไอดีเซิร์ฟเวอร์ของคุณ (ยังคงเก็บไว้ใช้ตามโค้ดเดิมของคุณ)
BotSever1 = 1204647300870311986 
BotSever2 = 1468565605836918846

# Event: เมื่อบอทออนไลน์สำเร็จ
@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Streaming(name="Phakaphop", url="https://www.twitch.tv/..."))
    print('Bot is ready.')

# ==================================================
# 🚀 โซนคำสั่งสำหรับพิมพ์คุย / สั่งบอทเข้าห้องโทร
# ==================================================

# 1. คำสั่ง !ping
@bot.command()
async def ping(ctx):
    await ctx.send("บอทออนไลน์และพร้อมรับคำสั่งแล้วครับ! 🚀")

# 2. คำสั่ง !hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"สวัสดีครับคุณ {ctx.author.name} ! 😊")


# 🛠️ 3. คำสั่งสั่งให้บอทเข้าห้องโทร (ห้องเสียงที่คนพิมพ์กำลังนั่งอยู่)
@bot.command()
async def join(ctx):
    # เช็กก่อนว่า คนพิมพ์คำสั่งได้นั่งอยู่ในห้องเสียงห้องไหนไหม
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        # สั่งให้บอทเชื่อมต่อเข้าห้องเสียงนั้น
        await channel.connect()
        await ctx.send(f"📥 เข้าห้องเสียง **{channel.name}** เรียบร้อยแล้วครับ!")
    else:
        # ถ้าคนพิมพ์ไม่ได้เข้าห้องเสียงอยู่ บอทจะแจ้งเตือน
        await ctx.send("❌ คุณต้องเข้าห้องเสียง (ห้องโทร) ก่อนสั่งคำสั่งนี้ครับ!")


# 🛠️ 4. คำสั่งสั่งให้บอทออกจากห้องโทร
@bot.command()
async def leave(ctx):
    # เช็กว่าบอทได้เปิดไมค์อยู่ในห้องเสียงของเซิร์ฟเวอร์นี้ไหม
    if ctx.voice_client:
        # สั่งให้บอทตัดการเชื่อมต่อออกมา
        await ctx.voice_client.disconnect()
        await ctx.send("📤 ออกจากห้องเสียงเรียบร้อยแล้วครับ!")
    else:
        await ctx.send("❌ ตอนนี้ผมไม่ได้อยู่ในห้องเสียงไหนเลยครับ")

# ==================================================
# 🛑 สั่งรันระบบทั้งหมด
# ==================================================
keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
