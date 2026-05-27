import nextcord
from nextcord.ext import commands
import os
import yt_dlp
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- ระบบเปิดพอร์ต 24 ชม. ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- ตั้งค่าบอท ---
load_dotenv()
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- ระบบเล่นเพลง ---
ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True}
ffmpeg_options = {'options': '-vn'}

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("📥 เข้าห้องแล้วครับ!")
    else:
        await ctx.send("❌ เข้าห้องเสียงก่อนนะครับ")

@bot.command()
async def play(ctx, *, url):
    if not ctx.voice_client:
        await ctx.invoke(join)
    
    async with ctx.typing():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await nextcord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
            ctx.voice_client.play(source)
    await ctx.send(f"🎵 กำลังเล่น: {info['title']}")

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send("📤 ออกแล้วครับ!")

bot.run(os.getenv('DISCORD_TOKEN'))
