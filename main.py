
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

# ไอดีเซิร์ฟเวอร์ของคุณ
BotSever1 = 1204647300870311986 
BotSever2 = 1468565605836918846

# Event: เมื่อบอทออนไลน์สำเร็จ
@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Streaming(name="Phakaphop", url="https://www.twitch.tv/..."))
    print('Bot is ready.')

# ==================================================
# 🚀 โซนคำสั่งสำหรับพิมพ์คุยใน Discord
# ==================================================

# 1. คำสั่ง !ping
@bot.command()
async def ping(ctx):
    await ctx.send("บอทออนไลน์และพร้อมรับคำสั่งแล้วครับ! 🚀")

# 2. คำสั่ง !hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"สวัสดีครับคุณ {ctx.author.name} ! 😊")


# 🛠️ 3. คำสั่งพิมพ์เพื่อเช็กคนเปิดสตรีมจอ (พิมพ์คำสั่ง !check)
@bot.command()
async def check(ctx):
    # รวมไอดีเซิร์ฟเวอร์ที่เราจะไปดึงข้อมูล
    server_ids = [BotSever1, BotSever2]
    streaming_users = []

    # วนลูปเช็กข้อมูลในเซิร์ฟเวอร์ที่บอทอยู่
    for server_id in server_ids:
        guild = bot.get_guild(server_id)
        if guild:
            # ค้นหาสมาชิกทุกคนที่อยู่ในห้องเสียงของเซิร์ฟเวอร์นั้น ๆ
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    # เช็กว่าสมาชิกคนนั้นเปิดสตรีมจอ (Share Screen) อยู่หรือไม่
                    if member.voice and member.voice.self_stream:
                        streaming_users.append(f"• **{member.name}** กำลังเปิดสตรีมจออยู่ในห้อง [ {voice_channel.name} ] ของเซิร์ฟเวอร์ *{guild.name}*")

    # สรุปผลลัพธ์และส่งข้อความตอบกลับเข้าดิสคอร์ด
    if streaming_users:
        result_text = "🎥 **รายชื่อคนที่กำลังเปิดสตรีมจออยู่ ณ ตอนนี้:**\n" + "\n".join(streaming_users)
        await ctx.send(result_text)
    else:
        await ctx.send("💤 ตอนนี้ไม่มีใครเปิดสตรีมจอในห้องเสียงเลยครับ")

# ==================================================
# 🛑 สั่งรันระบบทั้งหมด
# ==================================================
keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
