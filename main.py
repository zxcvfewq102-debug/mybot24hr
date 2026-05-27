import nextcord
from nextcord.ext import commands
import base64, codecs
import os
import urllib.request
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env (เพิ่มคำสั่งโหลดตรงนี้แล้วครับ)
load_dotenv()

# ตั้งค่าสิทธิ์การเข้าถึงให้บอท
intents = nextcord.Intents.all()
intents.message_content = True  
intents.voice_states = True     

# 🛑 จุดสำคัญ: ต้องใส่ intents=intents เข้าไปในวงเล็บนี้ด้วย บอทถึงจะยอมทำตามคำสั่งครับ
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

# 🚀 เพิ่มคำสั่งทดสอบพิมพ์ !ping เพื่อเช็กว่าบอทตอบสนองไหม
@bot.command()
async def ping(ctx):
    await ctx.send("บอทออนไลน์และพร้อมรับคำสั่งแล้วครับ! 🚀")

# เรียกใช้ตัวแปรจากระบบ Railway หรือไฟล์ .env
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
