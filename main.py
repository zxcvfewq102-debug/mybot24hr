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
def home(): return "Bot is running 24/7!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
Thread(target=run_web).start()

# --- ตั้งค่าบอท ---
load_dotenv()
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- ตั้งค่า yt-dlp พร้อม Cookies เพื่อแก้ปัญหา YouTube บล็อก ---
ydl_opts = {
    'format': 'bestaudio/best',
    'cookiefile': 'cookies.txt',  # <--- ใส่บรรทัดนี้เพื่อให้บอทใช้ไฟล์คุกกี้
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}
ffmpeg_options = {'options': '-vn -loglevel quiet'}

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        return await ctx.send("❌ ต้องอยู่ในห้องเสียงก่อนครับ")
    
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    
    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # ดึง URL สำหรับสตรีมเสียง
                url2 = info.get('url') or info.get('formats', [{}])[0].get('url')
                source = await nextcord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
                
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                
                ctx.voice_client.play(source)
                await ctx.send(f"🎵 กำลังเล่น: {info['title']}")
        except Exception as e:
            await ctx.send(f"❌ เกิดข้อผิดพลาด: {str(e)}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ หยุดเล่นเพลงแล้วครับ")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("📤 ออกจากห้องแล้วครับ")

bot.run(os.getenv('DISCORD_TOKEN'))
