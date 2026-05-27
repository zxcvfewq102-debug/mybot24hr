import discord
from discord.ext import commands
from discord.ui import Button, View
import yt_dlp
import asyncio
import time
import os

# --- ตั้งค่าสำหรับมือถือ ---
# ระบุ path ของ ffmpeg ให้ชัดเจน
FFMPEG_PATH = '/data/data/com.termux/files/usr/bin/ffmpeg' 
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
    'executable': FFMPEG_PATH # เพิ่มบรรทัดนี้เพื่อให้บอทหันไปใช้ ffmpeg ใน termux
}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

queues = {}

# ย่อขนาดการดึงข้อมูลเพื่อลดการใช้ RAM ในมือถือ
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data):
        super().__init__(source, volume=0.5)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url):
        data = await asyncio.to_thread(ytdl.extract_info, url, download=False)
        if 'entries' in data:
            data = data['entries'][0]
        # ใช้ FFMPEG_OPTIONS ที่กำหนดไว้ด้านบน
        return cls(discord.FFmpegPCMAudio(data['url'], **FFMPEG_OPTIONS), data=data)

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    if not ctx.author.voice:
        return await ctx.send("❌ เข้าห้องเสียงก่อนครับ")
    
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        player = await YTDLSource.from_url(query)
        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []
        queues[ctx.guild.id].append(player)

    if not ctx.voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(f"📥 เพิ่มเข้าคิว: {player.title}")

async def play_next(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        player = queues[ctx.guild.id].pop(0)
        ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f"🎵 กำลังเล่น: {player.title}")
    else:
        await ctx.voice_client.disconnect()

# ใส่ TOKEN ของคุณที่นี่
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
