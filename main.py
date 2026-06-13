import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import yt_dlp
import asyncio
import time
from datetime import datetime, timezone

# ตั้งค่า Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# สถานะบอท
queues = {}
now_playing = {}
control_messages = {}
start_times = {}

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'auto',
}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data):
        super().__init__(source, volume=0.5)
        self.title = data.get('title')
        self.webpage_url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration', 0)

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data: data = data['entries'][0]
        return cls(discord.FFmpegPCMAudio(data['url'], **FFMPEG_OPTIONS), data=data)

class MusicControlView(View):
    def __init__(self, interaction):
        super().__init__(timeout=None)
        self.interaction = interaction

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary)
    async def pause(self, interaction, button):
        if interaction.guild.voice_client: interaction.guild.voice_client.pause()
        await interaction.response.send_message("หยุดชั่วคราว", ephemeral=True)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        if interaction.guild.voice_client: interaction.guild.voice_client.resume()
        await interaction.response.send_message("เล่นต่อ", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'บอทเชื่อมต่อแล้ว: {bot.user}')

@bot.tree.command(name='play', description='เล่นเพลงจาก YouTube')
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    try:
        if not query.startswith('http'): query = f"ytsearch:{query}"
        player = await YTDLSource.from_url(query, loop=bot.loop)
        
        guild_id = interaction.guild.id
        if guild_id not in queues: queues[guild_id] = []
        queues[guild_id].append(player)
        
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await play_next(interaction)
            await interaction.followup.send(f"กำลังเล่น: {player.title}")
        else:
            await interaction.followup.send(f"เพิ่มเข้าคิว: {player.title}")
    except Exception as e:
        await interaction.followup.send(f"เกิดข้อผิดพลาด: 
        async def play_next(interaction):
    guild_id = interaction.guild.id
    if guild_id in queues and queues[guild_id]:
        player = queues[guild_id].pop(0)
        vc = interaction.guild.voice_client
        if not vc: vc = await interaction.user.voice.channel.connect()
        vc.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop))
    else:
        now_playing.pop(guild_id, None)

# เปลี่ยน token ตรงนี้
if __name__ == "__main__":
    bot.run('YOUR_BOT_TOKEN_HERE')
