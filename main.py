import nextcord
from nextcord.ext import commands
import base64, codecs
import os
import urllib.request
from dotenv import load_dotenv  # <-- เพิ่มบรรทัดนี้

# โหลดค่าจากไฟล์ .env
load_dotenv()  # <-- เพิ่มบรรทัดนี้

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.all()

bot = commands.Bot(command_prefix='!', help_command=None) # สมมติว่าของเดิมพิมพ์ตัดไป

BotSever1 = 1204647300870311986 
BotSever2 = 1468565605836918846 

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Streaming(name="Phakaphop", url="https://www.twitch.tv/..."))
    vc = nextcord.utils.get(bot.get_guild(BotSever1).voice_channels) # ปรับให้สมบูรณ์ขึ้น
    # await vc.guild.change_voice_state(...)
    print('Bot is ready.')

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.self_stream:
        print(f'{member.name} is in {after.channel.name}')

# 🛑 เปลี่ยนบรรทัดที่ 31 เดิม ให้เป็นเรียกใช้ตัวแปรจาก .env แบบนี้แทนครับ
TOKEN = os.getenv('DISCORD_TOKEN')
