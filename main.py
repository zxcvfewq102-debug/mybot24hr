import nextcord
from nextcord.ext import commands
import yt_dlp
import asyncio

# ตั้งค่า Intents สำหรับ Nextcord
intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

@bot.event
async def on_ready():
    print(f'🤖 บอทเพลงออนไลน์แล้ว (ระบบ Nextcord): {bot.user.name}')
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="!play [ชื่อเพลง]"))

@bot.command(aliases=['p'])
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ คุณต้องเข้าห้องเสียงก่อนสั่งเปิดเพลงนะ!")
    
    voice_channel = ctx.author.voice.channel

    if not ctx.voice_client:
        await voice_channel.connect()
    
    vc = ctx.voice_client
    await ctx.send(f"🔍 กำลังค้นหาเพลง: **{search}**...")

    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{search}", download=False))
        if 'entries' in data:
            data = data['entries'][0]
        
        song_url = data['url']
        song_title = data['title']
        
        if vc.is_playing():
            vc.stop()

        player = nextcord.FFmpegPCMAudio(song_url, **FFMPEG_OPTIONS)
        vc.play(player)
        
        await ctx.send(f"🎶 กำลังเล่นเพลง: **{song_title}**")
        
    except Exception as e:
        print(e)
        await ctx.send("❌ เกิดข้อผิดพลาด ไม่สามารถเปิดเพลงนี้ได้ครับ")

@bot.command(aliases=['leave'])
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 หยุดเล่นเพลงและออกจากห้องเสียงเรียบร้อยครับ")
    else:
        await ctx.send("❌ บอทไม่ได้อยู่ในห้องเสียงครับ")

# ⚠️ เอา Token ของคุณมาใส่ตรงนี้แทนข้อความด้านล่าง
import os
bot.run(os.getenv("MTIwOTMxOTU3MjIzNTA5MTk4OA.GCvb37.hBUCBcnTUjg6sR9QxyNahjGu8ITqZUyrSRAEBI"))
